import asyncio
import json
import tempfile
from pathlib import Path

import yt_dlp


def _json_to_netscape(json_path: Path) -> str:
    raw = json_path.read_text(encoding="utf-8").strip()
    if not raw.startswith("["):
        return ""
    cookies = json.loads(raw)
    lines = ["# Netscape HTTP Cookie File", "# Auto-converted from JSON by ttuploader"]
    for c in cookies:
        domain = c.get("domain", "")
        if not domain:
            continue
        initial_dot = "TRUE" if domain.startswith(".") else "FALSE"
        secure = "TRUE" if c.get("secure") else "FALSE"
        expires = str(int(float(c.get("expirationDate", 0))))
        path = c.get("path", "/")
        name = c.get("name", "")
        value = c.get("value", "")
        if name:
            lines.append(f"{domain}\t{initial_dot}\t{path}\t{secure}\t{expires}\t{name}\t{value}")
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8")
    tmp.write("\n".join(lines))
    tmp.close()
    return tmp.name


def _is_json_cookie(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8").strip()
        return text.startswith("[")
    except Exception:
        return False


def _should_cleanup(path: str) -> bool:
    return path.startswith(tempfile.gettempdir())


async def download_video(
    channel_url: str,
    download_dir: Path,
    archive_file: Path,
    proxy_url: str = "",
    cookie_file: str = "",
) -> str | None:
    normalized_url = channel_url.rstrip("/")
    if "@" in normalized_url and not any(s in normalized_url for s in ["/shorts", "/videos", "/live"]):
        normalized_url += "/shorts"

    download_dir.mkdir(parents=True, exist_ok=True)

    ydl_opts = {
        "format": (
            "best[width<=1080][height>=1920][ext=mp4]"
            "/best[width<=1080][ext=mp4]"
            "/best[ext=mp4]"
            "/best"
        ),
        "outtmpl": str(download_dir / "raw.%(ext)s"),
        "playlistend": 1,
        "quiet": True,
        "no_warnings": True,
        "merge_output_format": "mp4",
        "download_archive": str(archive_file),
    }

    if proxy_url:
        ydl_opts["proxy"] = proxy_url

    temp_cookie_path = None
    cookie_path = Path(cookie_file) if cookie_file else None
    if cookie_path and cookie_path.exists():
        if _is_json_cookie(cookie_path):
            temp_cookie_path = _json_to_netscape(cookie_path)
            ydl_opts["cookiefile"] = temp_cookie_path
        else:
            ydl_opts["cookiefile"] = cookie_file

    def _sync_download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([normalized_url])

    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, _sync_download)
    finally:
        if temp_cookie_path and Path(temp_cookie_path).exists():
            try:
                Path(temp_cookie_path).unlink()
            except Exception:
                pass

    mp4_path = download_dir / "raw.mp4"
    if mp4_path.exists():
        return str(mp4_path)

    found = list(download_dir.glob("raw.*"))
    for p in found:
        if p.suffix in (".mp4", ".mkv", ".webm", ".mov"):
            return str(p)

    return None
