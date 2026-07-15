import os
import re
from pathlib import Path
from dotenv import load_dotenv


def _parse_multiline_value(env_path: Path, key: str) -> str:
    content = env_path.read_text(encoding="utf-8")
    idx = content.find(f'{key}="')
    if idx == -1:
        return ""
    idx += len(f'{key}="')
    brace_depth = 0
    in_string = False
    escape = False
    for i in range(idx, len(content)):
        ch = content[i]
        if escape:
            escape = False
            continue
        if ch == "\\":
            escape = True
            continue
        if ch == '"' and not in_string:
            if brace_depth == 0:
                return content[idx:i]
            in_string = True
            continue
        if ch == '"' and in_string:
            in_string = False
            continue
        if not in_string:
            if ch in ("[", "{"):
                brace_depth += 1
            elif ch in ("]", "}"):
                brace_depth -= 1
    return content[idx:]


def _safe_int(raw: str, default: int) -> int:
    try:
        return int(raw)
    except (ValueError, TypeError):
        return default


class Settings:
    def __init__(self, env_file: str | None = None):
        env_path = Path(env_file) if env_file else Path(".env")
        if env_path.exists():
            load_dotenv(env_path)
        self._env_file = str(env_path)
        self._cookie_raw: str | None = None

    @property
    def google_api_key(self) -> str:
        return os.environ.get("GOOGLE_API_KEY", "")

    @property
    def channel_id(self) -> str:
        return os.environ.get("CHANNEL_ID", "")

    @property
    def min_check_interval(self) -> int:
        return _safe_int(os.environ.get("MINIMUM_CHECK_INTERVAL", "60"), 60)

    @property
    def max_check_interval(self) -> int:
        return _safe_int(os.environ.get("MAXIMUM_CHECK_INTERVAL", "300"), 300)

    @property
    def proxy(self) -> str:
        return os.environ.get("PROXY", "")

    @property
    def yt_cookie_file(self) -> str:
        return os.environ.get("YT_COOKIE_FILE", "")

    @property
    def skip_duration_more_than(self) -> int:
        return _safe_int(os.environ.get("SKIP_VIDEO_IF_DURATION_MORE_THAN", "300"), 300)

    @property
    def skip_duration_less_than(self) -> int:
        return _safe_int(os.environ.get("SKIP_VIDEO_IF_DURATION_LESS_THAN", "0"), 0)

    @property
    def render_strategy(self) -> str:
        return os.environ.get("RENDER_STRATEGY", "stealth")

    @property
    def audio_render_strategy(self) -> str:
        return os.environ.get("AUDIO_RENDER_STRATEGY", "pitch_speedshift")

    @property
    def minimum_video_duration(self) -> int:
        return _safe_int(os.environ.get("MINIMUM_VIDEO_DURATION", "0"), 0)

    @property
    def tiktok_region(self) -> str:
        return os.environ.get("TIKTOK_REGION", "US")

    @property
    def tiktok_cookie(self) -> str:
        if self._cookie_raw is not None:
            return self._cookie_raw

        cookie_file = os.environ.get("TIKTOK_COOKIE_FILE", "")
        if cookie_file and Path(cookie_file).exists():
            self._cookie_raw = Path(cookie_file).read_text(encoding="utf-8")
            return self._cookie_raw

        env_val = os.environ.get("TIKTOK_COOKIE", "")
        if env_val and env_val.strip().startswith(("[", "{")):
            self._cookie_raw = env_val
            return env_val

        env_path = Path(self._env_file)
        if env_path.exists():
            multi = _parse_multiline_value(env_path, "TIKTOK_COOKIE")
            if multi:
                if multi.endswith(".json") and Path(multi).exists():
                    self._cookie_raw = Path(multi).read_text(encoding="utf-8")
                else:
                    self._cookie_raw = multi
                return self._cookie_raw

        if env_val.endswith(".json") and Path(env_val).exists():
            self._cookie_raw = Path(env_val).read_text(encoding="utf-8")
            return self._cookie_raw

        return env_val

    @property
    def discord_webhook_url(self) -> str:
        return os.environ.get("DISCORD_WEBHOOK_URL", "")

    @property
    def fallback_caption(self) -> str:
        return os.environ.get("FALLBACK_CAPTION", "")

    @property
    def fallback_hashtags(self) -> str:
        return os.environ.get("FALLBACK_HASHTAGS", "#viral #trending #fyp")
