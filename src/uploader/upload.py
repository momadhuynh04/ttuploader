import asyncio
import os
import random
import time
from pathlib import Path

from src.i18n.base import get_locale
from src.logger.pipeline import PipelineLog
from src.renderer.runner import render_video
from src.uploader.browser import BrowserSession
from src.uploader.popups import dismiss_popups


async def _check_success(page, locale: dict) -> bool:
    if any(p in page.url.lower() for p in locale.get("success_url_patterns", [])):
        return True
    success_signs = [
        "button:has-text('Quản lý bài đăng')",
        "button:has-text('Manage posts')",
        "button:has-text('Tải video khác lên')",
        "button:has-text('Upload another video')",
        "div:has-text('Đã đăng lên')",
        "div:has-text('Uploaded')",
    ]
    all_selectors = success_signs + locale.get("success_selectors", [])
    for sel in all_selectors:
        try:
            el = page.locator(sel).first
            if await el.count() > 0 and await el.is_visible():
                return True
        except Exception:
            pass
    return False


def _parse_hashtags(raw: str) -> list[str]:
    return [h.strip() for h in raw.replace("\n", ",").split(",") if h.strip()]


async def upload_to_tiktok(
    browser: BrowserSession,
    video_path: str,
    download_dir: Path,
    caption_template: str,
    hashtags_raw: str,
    render_strategy: str,
    audio_strategy: str,
    pipeline_log: PipelineLog,
) -> bool:
    t0 = time.time()
    locale = get_locale(browser.region)
    page = browser.page

    rendered_path, render_time = await render_video(
        video_path, download_dir, render_strategy, audio_strategy
    )
    pipeline_log.render_time = render_time
    pipeline_log.render_strategy = render_strategy
    pipeline_log.render_before_mb = os.path.getsize(video_path) / (1024 * 1024)
    pipeline_log.render_after_mb = os.path.getsize(rendered_path) / (1024 * 1024)

    t_nav_start = time.time()
    try:
        await page.goto(
            "https://www.tiktok.com/tiktokstudio/upload",
            wait_until="domcontentloaded",
            timeout=30000,
        )
    except Exception:
        try:
            await page.goto(
                "https://www.tiktok.com/tiktokstudio/upload",
                wait_until="load",
                timeout=60000,
            )
        except Exception as e:
            pipeline_log.error = f"Navigation failed: {e}"
            return False
    pipeline_log.upload_nav_time = time.time() - t_nav_start

    if "login" in page.url.lower():
        pipeline_log.error = "Cookie expired - redirect to login"
        return False

    await dismiss_popups(page, locale["popup_dismiss_selectors"])
    await asyncio.sleep(0.5)

    await browser.disable_file_picker()

    t_file_start = time.time()
    try:
        upload_selectors = locale["upload_button_selectors"]
        upload_btn = page.locator(", ".join(upload_selectors)).first
        await upload_btn.wait_for(state="visible", timeout=15000)

        async with page.expect_file_chooser(timeout=15000) as fc_info:
            await upload_btn.click(delay=100)
        file_chooser = await fc_info.value
        await file_chooser.set_files(rendered_path)
        pipeline_log.upload_file_time = time.time() - t_file_start
    except Exception as e:
        err_path = str(download_dir / "error_priming_upload.png")
        try:
            await page.screenshot(path=err_path)
        except Exception:
            pass
        pipeline_log.error = f"File injection failed: {e}"
        return False

    editor_selectors = locale["caption_editor_selectors"]
    editor = page.locator(", ".join(editor_selectors)).first
    await editor.wait_for(state="visible", timeout=30000)
    await asyncio.sleep(1)

    await dismiss_popups(page, locale["popup_dismiss_selectors"])

    t_cap_start = time.time()
    parsed_caption = caption_template.strip() if caption_template else ""
    hashtags_list = _parse_hashtags(hashtags_raw)
    k = min(10, len(hashtags_list))
    selected_tags = random.sample(hashtags_list, k=k) if k > 0 else []
    full_cap = f"{parsed_caption} {' '.join(selected_tags)}".strip()

    await editor.fill(full_cap)
    pipeline_log.upload_caption_time = time.time() - t_cap_start

    t_post_start = time.time()
    post_selectors = locale["post_button_selectors"]
    force_post_selectors = locale["force_post_selectors"]
    success_posted = False

    file_size_mb = os.path.getsize(rendered_path) / (1024 * 1024)
    max_iterations = max(300, int(file_size_mb * 6))

    for i in range(max_iterations):
        try:
            if await _check_success(page, locale):
                success_posted = True
                break

            for sel in post_selectors:
                btn = page.locator(sel).last
                if await btn.count() > 0 and await btn.is_visible():
                    await btn.hover()
                    await btn.click(force=True)
                    if i % 10 == 0:
                        print("[*] Clicked post button, waiting...", flush=True)
                    break

            for fps in force_post_selectors:
                force_btn = page.locator(fps).last
                if await force_btn.count() > 0 and await force_btn.is_visible():
                    await force_btn.click(force=True)
                    print(f"[*] Dismissed force-post popup: {fps}", flush=True)
                    break
        except Exception:
            pass

        await asyncio.sleep(0.1)

    pipeline_log.upload_post_wait_time = time.time() - t_post_start
    pipeline_log.upload_total_time = time.time() - t0

    if not success_posted:
        err_path = str(download_dir / "error_post_failed.png")
        try:
            await page.screenshot(path=err_path)
        except Exception:
            pass
        pipeline_log.error = "Post timeout - upload may have failed"
        return False

    return True
