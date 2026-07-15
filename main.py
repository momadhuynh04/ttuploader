import asyncio
import os
import random
import signal
import sys
import time
from pathlib import Path

from src.cli.parser import build_parser
from src.config.settings import Settings
from src.storage.session import SessionStorage
from src.logger.pipeline import PipelineLogger
from src.logger.discord_webhook import send_discord_webhook, send_discord_startup, send_discord_shutdown
from src.youtube.api import YouTubeAPI
from src.downloader.ytdlp import download_video
from src.uploader.browser import BrowserSession
from src.uploader.upload import upload_to_tiktok


shutdown_event = asyncio.Event()


def _setup_signal_handlers():
    try:
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGINT, shutdown_event.set)
        loop.add_signal_handler(signal.SIGTERM, shutdown_event.set)
    except (NotImplementedError, RuntimeError):
        pass


def cleanup_workspace(download_dir: Path):
    for f in download_dir.glob("*"):
        if f.is_file():
            try:
                f.unlink()
            except Exception as e:
                print(f"[!] Cleanup warning: {e}", flush=True)


async def _sleep_interruptible(seconds: float):
    interval = 0.5
    elapsed = 0.0
    while elapsed < seconds:
        if shutdown_event.is_set():
            return
        await asyncio.sleep(min(interval, seconds - elapsed))
        elapsed += interval


async def run_bot(settings: Settings, session_name: str, headless: bool, interval_override: int | None):
    _setup_signal_handlers()
    storage = SessionStorage(session_name)
    pipeline_logger = PipelineLogger(session_name)

    storage.state.region = settings.tiktok_region
    storage.state.env_file = str(settings._env_file)
    storage.save_state()

    print("\n" + "=" * 50, flush=True)
    print(f"[*] ttuploader — BOT KHỞI ĐỘNG", flush=True)
    print(f"[*] Session  : {session_name}", flush=True)
    print(f"[*] Region   : {settings.tiktok_region}", flush=True)
    print(f"[*] Channel  : {settings.channel_id}", flush=True)
    print(f"[*] Render   : {settings.render_strategy} / {settings.audio_render_strategy}", flush=True)
    print(f"[*] Proxy    : {'Có' if settings.proxy else 'Không'}", flush=True)
    print(f"[*] Discord  : {'Có' if settings.discord_webhook_url else 'Không'}", flush=True)
    print("=" * 50 + "\n", flush=True)

    await send_discord_startup(
        settings.discord_webhook_url, session_name, settings.tiktok_region
    )

    if not settings.google_api_key:
        print("[!] GOOGLE_API_KEY chưa được set trong .env", flush=True)
        return
    if not settings.channel_id:
        print("[!] CHANNEL_ID chưa được set trong .env", flush=True)
        return

    youtube_api = YouTubeAPI(settings.google_api_key)
    channel_id = await youtube_api.resolve_channel_id(settings.channel_id)
    print(f"[*] Channel ID resolved: {channel_id}", flush=True)

    browser = BrowserSession(
        proxy_url=settings.proxy,
        region=settings.tiktok_region,
        cookie_raw=settings.tiktok_cookie,
        headless=headless,
    )
    await browser.launch()
    print("[*] Browser launched — sống đến khi tắt CLI", flush=True)

    download_dir = storage.get_download_dir()
    quota_backoff = 0

    try:
        while not shutdown_event.is_set():
            cleanup_workspace(download_dir)

            if quota_backoff > 0:
                print(f"[!] API quota exceeded, sleeping {quota_backoff}s...", flush=True)
                await _sleep_interruptible(quota_backoff)
                quota_backoff = min(quota_backoff * 2, 86400)

            print(f"\n[*] Checking for new Shorts...", flush=True)
            check_start = time.time()

            try:
                videos = await youtube_api.get_latest_shorts(channel_id, max_results=5)
                quota_backoff = 0
            except Exception as e:
                err_msg = str(e)
                print(f"[!] YouTube API error: {e}", flush=True)
                if "quota" in err_msg.lower() or "429" in err_msg:
                    quota_backoff = max(quota_backoff, 3600)
                await _sleep_interruptible(settings.min_check_interval)
                continue
            check_time = time.time() - check_start

            new_video = None
            for vid in videos:
                if vid.duration_seconds > settings.skip_duration_more_than or vid.duration_seconds < settings.skip_duration_less_than:
                    continue
                if not storage.is_uploaded(vid.video_id):
                    new_video = vid
                    break

            if new_video is None:
                uploaded_ids = storage.get_uploaded_ids()
                if videos:
                    latest = videos[0]
                    if latest.video_id in uploaded_ids:
                        print(f"[*] Latest video {latest.video_id} already uploaded. Skipping.", flush=True)
                    else:
                        print("[*] No new Shorts found.", flush=True)
                else:
                    print("[*] No Shorts found on channel.", flush=True)

                interval = interval_override or random.randint(
                    settings.min_check_interval, settings.max_check_interval
                )
                print(f"[*] Sleeping {interval}s...", flush=True)
                try:
                    await browser.goto("https://www.tiktok.com/tiktokstudio/upload")
                except Exception:
                    pass
                await _sleep_interruptible(interval)
                continue

            log = pipeline_logger.new_log()
            log.video_id = new_video.video_id
            log.video_title = new_video.title
            log.video_duration = new_video.duration_seconds
            log.check_time = check_time

            print(f"[*] NEW VIDEO: {new_video.title} ({new_video.duration_seconds:.0f}s)", flush=True)

            pipeline_start = time.time()

            dl_start = time.time()
            try:
                raw_path = await download_video(
                    channel_url=f"https://www.youtube.com/shorts/{new_video.video_id}",
                    download_dir=download_dir,
                    archive_file=storage.archive_file,
                    cookie_file=settings.yt_cookie_file,
                )
            except Exception as e:
                log.download_time = time.time() - dl_start
                log.error = f"Download failed: {e}"
                log.total_time = time.time() - pipeline_start
                log.success = False
                print(f"[✗] Download error: {e}", flush=True)
                pipeline_logger.flush()
                await send_discord_webhook(settings.discord_webhook_url, log)
                await _sleep_interruptible(settings.min_check_interval)
                continue
            log.download_time = time.time() - dl_start

            if raw_path is None:
                print("[*] Already archived — marking as done.", flush=True)
                storage.mark_uploaded(new_video.video_id)
                pipeline_logger.flush()
                interval = interval_override or random.randint(
                    settings.min_check_interval, settings.max_check_interval
                )
                print(f"[*] Sleeping {interval}s before next check...", flush=True)
                await _sleep_interruptible(interval)
                continue

            log.download_size_mb = os.path.getsize(raw_path) / (1024 * 1024)
            print(f"[*] Downloaded: {log.download_size_mb:.1f} MB", flush=True)

            success = await upload_to_tiktok(
                browser=browser,
                video_path=raw_path,
                download_dir=download_dir,
                caption_template=settings.fallback_caption or new_video.title,
                hashtags_raw=settings.fallback_hashtags,
                render_strategy=settings.render_strategy,
                audio_strategy=settings.audio_render_strategy,
                pipeline_log=log,
            )

            log.total_time = time.time() - pipeline_start
            log.success = success

            console_output = pipeline_logger.format_console(log)
            print("\n" + console_output + "\n", flush=True)
            pipeline_logger.flush()

            if success:
                storage.mark_uploaded(new_video.video_id)
                print(f"[✓] Upload thành công! Total: {storage.state.total_uploaded} videos.", flush=True)
                await browser.goto("https://www.tiktok.com/tiktokstudio/upload")
            else:
                storage.mark_failed()
                print(f"[✗] Upload thất bại.", flush=True)

            await send_discord_webhook(settings.discord_webhook_url, log)

            if interval_override is not None:
                if interval_override == 0:
                    break

            interval = interval_override or random.randint(
                settings.min_check_interval, settings.max_check_interval
            )
            print(f"[*] Sleeping {interval}s...", flush=True)
            await _sleep_interruptible(interval)

    finally:
        print("\n[*] Shutting down browser...", flush=True)
        await browser.close()
        storage.save_state()
        await send_discord_shutdown(
            settings.discord_webhook_url,
            session_name,
            storage.state.total_uploaded,
        )
        print(f"[*] Session saved. Total uploaded: {storage.state.total_uploaded}", flush=True)
        print("[*] Goodbye!", flush=True)


async def main():
    parser = build_parser()
    args = parser.parse_args()

    if not Path(args.env).exists():
        print(f"[!] Env file not found: {args.env}", flush=True)
        sys.exit(1)

    settings = Settings(args.env)

    interval = args.interval
    if args.once:
        interval = 0

    await run_bot(
        settings=settings,
        session_name=args.session,
        headless=args.headless,
        interval_override=interval,
    )


if __name__ == "__main__":
    asyncio.run(main())
