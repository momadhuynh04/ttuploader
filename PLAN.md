# PLAN.md — ttuploader Development Plan

> **Mục tiêu:** Tự động hóa pipeline YouTube Short → TikTok với Phantomwright anti-detection, đa ngôn ngữ, đa session.

---

## 1. Tổng quan Kiến trúc

```
┌─────────────────────────────────────────────────────────────────────┐
│                          MAIN CLI LOOP                               │
│                   python main.py --env .env --session ws1            │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  1. Load Config (.env)    │  2. Init Storage (per session)           │
│  3. Start Browser         │  4. Enter Pipeline Loop                  │
└─────────────────────────────────────────────────────────────────────┘
```

### Pipeline Sequence Diagram (UML)

```
┌──────────┐  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌──────────┐
│  CLI     │  │  Config  │  │  Storage  │  │ YouTube  │  │ Downloader│  │ Renderer │  │ Uploader │
│  (main)  │  │ (.env)   │  │ (session) │  │ API v3   │  │ (yt-dlp)  │  │ (FFmpeg) │  │(Phantomw)│
└────┬─────┘  └────┬─────┘  └─────┬─────┘  └────┬─────┘  └─────┬─────┘  └────┬─────┘  └────┬─────┘
     │              │              │              │              │              │              │
     │ parse_args() │              │              │              │              │              │
     │─────────────►│              │              │              │              │              │
     │              │              │              │              │              │              │
     │ load_env()   │              │              │              │              │              │
     │◄─────────────│              │              │              │              │              │
     │              │              │              │              │              │              │
     │ init_session(session_name)  │              │              │              │              │
     │─────────────────────────────►              │              │              │              │
     │              │              │              │              │              │              │
     │              │     Load uploaded.txt       │              │              │              │
     │              │     Load session.json       │              │              │              │
     │              │◄─────────────────────────────              │              │              │
     │              │              │              │              │              │              │
     │ launch_browser(proxy, stealth, locale)───────────────────────────────────────────────►
     │              │              │              │              │              │              │
     │╔══════════════ P I P E L I N E   L O O P ═══════════════╗│              │              │
     │║            │              │              │              │              │              │
     │║ check_videos(channel_id, api_key)────────►              │              │              │
     │║            │              │              │              │              │              │
     │║            │              │   is_new(video_id)?         │              │              │
     │║            │              │◄─────────────────────────────              │              │
     │║            │              │              │              │              │              │
     │║  [if NEW]  │              │              │ download(url, proxy)        │              │
     │║─────────────────────────────────────────────────────────►              │              │
     │║            │              │              │              │              │              │
     │║            │              │              │              │ raw_video.mp4│              │
     │║            │◄─────────────────────────────────────────────────────────              │
     │║            │              │              │              │              │              │
     │║  render(strategy, audio_strategy) ────────────────────────────────────►              │
     │║            │              │              │              │              │              │
     │║            │              │              │              │  processed.mp4              │
     │║            │◄────────────────────────────────────────────────────────              │
     │║            │              │              │              │              │              │
     │║  upload_to_tiktok(video, caption, hashtags) ─────────────────────────────────────────►
     │║            │              │              │              │              │              │
     │║            │              │              │              │              │  success/fail│
     │║            │◄────────────────────────────────────────────────────────────────────────
     │║            │              │              │              │              │              │
     │║  save_uploaded(video_id) ─►              │              │              │              │
     │║            │              │              │              │              │              │
     │║  log_to_discord(pipeline_stats) ─────────────────────────────────────────────────────►
     │║            │              │              │              │              │              │
     │╚════════════ sleep(random 3-5h) ─────────────────────────╝              │              │
     │              │              │              │              │              │              │
```

---

## 2. Cấu trúc Thư mục

```
ttuploader/
│
├── main.py                          # CLI entry point
├── requirements.txt                 # Python dependencies
├── runtime/                         # Python venv (gitignored)
│
├── src/
│   ├── __init__.py
│   │
│   ├── config/                      # ── Config + Env ──
│   │   ├── __init__.py
│   │   └── settings.py              # Load .env, parse all env vars
│   │
│   ├── youtube/                     # ── YouTube API v3 ──
│   │   ├── __init__.py
│   │   └── api.py                   # Google API client, check latest Shorts
│   │
│   ├── downloader/                  # ── yt-dlp ──
│   │   ├── __init__.py
│   │   └── ytdlp.py                 # Download wrapper, archive tracking
│   │
│   ├── renderer/                    # ── FFmpeg Render ──
│   │   ├── __init__.py
│   │   ├── strategies.py            # Stealth / Loop / Transform strategies
│   │   ├── audio.py                 # Pitch+Speed / Enhanced / Re-encode / Replace / NoSound
│   │   └── runner.py                # FFmpeg process runner, GPU/CPU detect
│   │
│   ├── uploader/                    # ── Phantomwright ──
│   │   ├── __init__.py
│   │   ├── browser.py               # Browser launch, proxy, cookie, lifecycle
│   │   ├── stealth_setup.py         # Stealth fingerprint evasion config
│   │   ├── upload.py                # Upload flow: navigate → file → caption → post
│   │   ├── popups.py                # Popup dismiss handlers per region
│   │   └── success_detect.py        # Upload success detection logic
│   │
│   ├── storage/                     # ── Data Persistence ──
│   │   ├── __init__.py
│   │   ├── session.py               # Session state management (create, load, save)
│   │   └── uploaded.py              # Uploaded video ID tracker (txt file)
│   │
│   ├── logger/                      # ── Logging + Discord ──
│   │   ├── __init__.py
│   │   ├── pipeline.py              # Pipeline step timing, video metadata logger
│   │   └── discord_webhook.py       # Discord webhook sender (embed format)
│   │
│   ├── i18n/                        # ── Multi-language ──
│   │   ├── __init__.py
│   │   ├── base.py                  # Region → locale mapping + UI selectors
│   │   └── locales/
│   │       ├── en.py                # English (US)
│   │       ├── vn.py                # Vietnamese (VN)
│   │       ├── jp.py                # Japanese (JP)
│   │       ├── kr.py                # Korean (KR)
│   │       ├── br.py                # Portuguese (BR)
│   │       ├── it.py                # Italian (IT)
│   │       ├── fr.py                # French (FR)
│   │       ├── de.py                # German (DE)
│   │       └── es.py                # Spanish (ES)
│   │
│   └── cli/                         # ── CLI Interface ──
│       ├── __init__.py
│       └── parser.py                # argparse setup, session/env selection
│
├── data/                            # Data directory (gitignored partial)
│   └── sessions/
│       └── {session_name}/          # e.g. "workspace_us", "workspace_vn"
│           ├── uploaded.txt         # List of uploaded YouTube video IDs
│           └── session.json         # Session runtime state
│
├── logs/                            # Log files (gitignored)
│   └── {session_name}/
│       └── {YYYY-MM-DD}.log
│
├── downloads/                       # Temp video workspace (gitignored)
│
├── .env                             # Default env (gitignored)
├── .env.example                     # Env template (committed)
└── .python-version                  # Python 3.11.9
```

---

## 3. Thiết lập Môi trường (venv + requirements.txt)

### Tạo virtual environment

```powershell
# Tạo venv tên "runtime" (theo AGENTS.md)
python -m venv runtime

# Activate (Windows)
.\runtime\Scripts\Activate.ps1

# Activate (Linux/Mac)
source runtime/bin/activate
```

### requirements.txt

```
# ── Browser Automation (BẮT BUỘC) ──
phantomwright>=0.2.0

# ── Video Download ──
yt-dlp>=2024.0.0

# ── Google API ──
google-api-python-client>=2.0.0

# ── Config ──
python-dotenv>=1.0.0

# ── Discord Webhook ──
aiohttp>=3.9.0          # (đã bundled với phantomwright)

# ── Image Processing (Captcha fallback) ──
opencv-python>=4.8.0
numpy>=1.24.0
```

Cài đặt:

```bash
pip install -r requirements.txt
phantomwright_driver install chromium
```

---

## 4. CLI Usage

### Command

```bash
python main.py --env <env_file> --session <session_name> [options]
```

### Arguments

| Flag | Required | Default | Mô tả |
|------|----------|---------|-------|
| `--env` | Yes | `.env` | Path to .env file |
| `--session` | Yes | — | Session name (tạo thư mục `data/sessions/{session}/`) |
| `--headless` | No | `false` | Chạy browser headless (ẩn cửa sổ) |
| `--once` | No | `false` | Chạy 1 lần rồi thoát (không loop) |
| `--interval` | No | (từ .env) | Override check interval (seconds) |

### Ví dụ

```bash
# Chạy bot với file env riêng, session "workspace_vn", show browser
python main.py --env .env.prod --session workspace_vn

# Chạy headless, chỉ 1 lần
python main.py --env .env --session test_run --headless --once
```

### Flow khi chạy CLI

```
1. Parse args            → lấy --env, --session
2. Load .env             → đọc toàn bộ biến môi trường
3. Init session storage  → tạo data/sessions/{session_name}/ nếu chưa có
                           → load uploaded.txt (danh sách ID đã upload)
                           → load/create session.json (trạng thái phiên)
4. Launch Browser        → mở Phantomwright Chromium với proxy + stealth
                           → trình duyệt SỐNG đến khi tắt CLI (Ctrl+C)
5. Pipeline Loop         → check → download → render → upload → log → sleep
6. On Exit (Ctrl+C)      → save session state → close browser → log summary
```

---

## 5. Chi tiết Env Variables (`.env`)

Tham chiếu đầy đủ từ `.env.example`:

### 5.1 YouTube API

| Biến | Mô tả | Ví dụ |
|------|-------|-------|
| `GOOGLE_API_KEY` | API Key YouTube Data API v3 | `AIzaSy...` |
| `CHANNEL_ID` | ID hoặc URL kênh YouTube | `https://www.youtube.com/@channel/shorts` |
| `MINIMUM_CHECK_INTERVAL` | Thời gian check tối thiểu (giây) | `60` |
| `MAXIMUM_CHECK_INTERVAL` | Thời gian check tối đa (giây) | `300` |

> **Cách lấy GOOGLE_API_KEY:**
> 1. Vào [Google Cloud Console](https://console.cloud.google.com/)
> 2. Tạo Project → Enable "YouTube Data API v3"
> 3. Credentials → Create API Key
> 4. Copy key vào .env

> **Check interval:** Mỗi chu kỳ sẽ random 1 số trong khoảng `[MIN, MAX]` để sleep. Ví dụ: `60-300` → bot check mỗi 1-5 phút.

### 5.2 Proxy

| Biến | Mô tả | Format |
|------|-------|--------|
| `PROXY` | Proxy string cho browser | `socks5://user:pass@host:port` |

> **Không datacenter IP.** Chỉ dùng residential/mobile proxy. Để trống nếu không dùng proxy.
> Hỗ trợ: `http://`, `https://`, `socks5://`

### 5.3 Render Strategy

| Biến | Default | Options |
|------|---------|---------|
| `RENDER_STRATEGY` | `stealth` | `none` / `stealth` / `loop` / `transform` |
| `AUDIO_RENDER_STRATEGY` | `pitch_speedshift` | `none` / `pitch_speedshift` / `enhanced_pitch` / `re_encode` / `audio_mix` / `full_replace` / `no_sound` |
| `MINIMUM_VIDEO_DURATION` | `0` | Số giây tối thiểu, video ngắn hơn sẽ bị skip |

> **Render Strategy chi tiết:**
> - `none`: Không render, giữ nguyên video gốc
> - `stealth`: hflip + crop 3% + color shift + speed 2% + metadata strip (nhanh, ~2-3s/30s video)
> - `loop`: Play 2 lần với color grading khác mỗi nửa
> - `transform`: Stealth + text overlay (@handle) + border padding

> **Audio Strategy chi tiết:**
> - `none`: Giữ nguyên audio
> - `pitch_speedshift`: Pitch ±3% + speed ±2%
> - `enhanced_pitch`: Pitch shift mạnh hơn ±8%
> - `re_encode`: Re-encode audio stream
> - `audio_mix`: Mix với white noise nhẹ
> - `full_replace`: Thay toàn bộ audio = audio từ thư viện
> - `no_sound`: Xóa hoàn toàn audio

### 5.4 TikTok Region & Cookie

| Biến | Mô tả | Options |
|------|-------|---------|
| `TIKTOK_REGION` | Region TikTok account | `US`, `JP`, `KR`, `VN`, `BR`, `IT`, `FR`, `DE`, `ES` |
| `TIKTOK_COOKIE` | Cookie string TikTok (JSON hoặc Base64) | Xem bên dưới |

> **TIKTOK_COOKIE format:**
> ```json
> [{"name":"sessionid","value":"...","domain":".tiktok.com","path":"/","httpOnly":true,"secure":true,"sameSite":"None"}]
> ```
> Hoặc Base64 encode của JSON trên.

> **Region → Automation Language mapping:**
>
> | Region | Ngôn ngữ UI | Browser locale | TikTok UI language |
> |--------|-------------|----------------|-------------------|
> | `US` | English | `en-US` | English |
> | `JP` | 日本語 | `ja-JP` | Japanese |
> | `KR` | 한국어 | `ko-KR` | Korean |
> | `VN` | Tiếng Việt | `vi-VN` | Vietnamese |
> | `BR` | Português | `pt-BR` | Portuguese |
> | `IT` | Italiano | `it-IT` | Italian |
> | `FR` | Français | `fr-FR` | French |
> | `DE` | Deutsch | `de-DE` | German |
> | `ES` | Español | `es-ES` | Spanish |

### 5.5 Discord & Caption

| Biến | Mô tả |
|------|-------|
| `DISCORD_WEBHOOK_URL` | Discord webhook URL để gửi log |
| `FALLBACK_CAPTION` | Caption mặc định nếu không extract được từ YouTube |
| `FALLBACK_HASHTAGS` | Hashtags mặc định, phân cách bằng dấu phẩy |

---

## 6. YouTube API v3 Integration (`src/youtube/api.py`)

### Chức năng

- Gọi API `search.list` để tìm Short mới nhất của channel
- Gọi API `videos.list` để lấy metadata (title, duration, publish date)
- So sánh với `uploaded.txt` (per session) để xác định video mới

### API Flow

```
1. Resolve Channel ID từ URL (nếu input là URL)
   GET https://www.googleapis.com/youtube/v3/search?part=snippet&q={handle}&type=channel&key={API_KEY}

2. Lấy Shorts mới nhất
   GET https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={ID}&type=video&videoDuration=short&order=date&maxResults=5&key={API_KEY}

3. Lấy metadata từng video
   GET https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails,statistics&id={VIDEO_ID}&key={API_KEY}

4. Filter:
   - Chỉ lấy video duration < 60s (YouTube Shorts)
   - Bỏ qua nếu video_id đã có trong data/sessions/{session}/uploaded.txt
   - Trả về video mới nhất chưa upload
```

### Module Structure

```python
# src/youtube/api.py

class YouTubeAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def resolve_channel_id(self, channel_input: str) -> str:
        """Resolve channel URL or @handle to channel ID"""
        ...

    def get_latest_shorts(self, channel_id: str, max_results: int = 5) -> list[VideoMeta]:
        """Get latest Shorts from channel"""
        ...

    def get_video_meta(self, video_id: str) -> VideoMeta:
        """Get full metadata for a video"""
        ...
```

---

## 7. Session Storage (`src/storage/`)

### Nguyên tắc

- **Mỗi session có thư mục riêng:** `data/sessions/{session_name}/`
- **uploaded.txt:** Lưu mỗi dòng 1 `video_id` đã upload thành công
- **session.json:** Lưu trạng thái runtime (lần check cuối, số video đã upload, etc.)

### uploaded.txt format

```
dQw4w9WgXcQ
9bZkp7q19f0
jNQXAC9IVRw
```

### session.json format

```json
{
  "session_name": "workspace_vn",
  "created_at": "2026-07-15T10:00:00+07:00",
  "last_check": "2026-07-15T14:30:00+07:00",
  "total_uploaded": 42,
  "total_failed": 3,
  "region": "VN",
  "env_file": ".env.prod"
}
```

### Code

```python
# src/storage/session.py

class SessionStorage:
    def __init__(self, session_name: str):
        self.session_dir = Path("data/sessions") / session_name
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.uploaded_file = self.session_dir / "uploaded.txt"
        self.state_file = self.session_dir / "session.json"
        self.state = self._load_state()

    def is_uploaded(self, video_id: str) -> bool:
        """Check if video_id already in uploaded.txt"""
        ...

    def mark_uploaded(self, video_id: str):
        """Append video_id to uploaded.txt"""
        ...

    def save_state(self):
        """Write session.json"""
        ...
```

---

## 8. Phantomwright Anti-Detection Setup

### 8.1 Browser Launch

```python
from phantomwright.async_api import async_playwright
from phantomwright.stealth import Stealth

async def create_browser(proxy_url: str, region: str):
    async with async_playwright() as pw:
        # 1. Parse proxy
        proxy = None
        if proxy_url:
            parsed = urlparse(proxy_url)
            proxy = {
                "server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}",
                "username": parsed.username,
                "password": parsed.password,
            }

        # 2. Launch browser
        browser = await pw.chromium.launch(
            headless=False,
            proxy=proxy,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",  # Ẩn automation flag
                "--disable-infobars",
            ],
        )

        # 3. Context với locale theo region
        locale_map = {
            "US": "en-US", "JP": "ja-JP", "KR": "ko-KR", "VN": "vi-VN",
            "BR": "pt-BR", "IT": "it-IT", "FR": "fr-FR", "DE": "de-DE", "ES": "es-ES",
        }
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale=locale_map.get(region, "en-US"),
        )

        # 4. Áp dụng Stealth fingerprint evasion
        stealth = Stealth(
            navigator_webdriver=True,          # Ghi đè navigator.webdriver = false
            navigator_languages_override=...,   # Khớp với locale
        )
        await stealth.apply_stealth_async(context)

        # 5. Inject cookies nếu có
        if cookies:
            await context.add_cookies(cookies)

        page = await context.new_page()
        return browser, context, page
```

### 8.2 Stealth Config chi tiết

Các evasion chính được bật:

| Evasion | Mô tả |
|---------|-------|
| `navigator_webdriver` | `navigator.webdriver` = `false` |
| `navigator_languages` | Khớp locale region |
| `navigator_plugins` | Fake plugin list |
| `navigator_hardware_concurrency` | Fake CPU cores |
| `chrome_runtime` | Ẩn `chrome.runtime` |
| `iframe_content_window` | Giả lập iframe |

### 8.3 Browser Lifecycle

```
CLI start
  │
  ├─► Launch browser (headful, proxy, stealth)
  │     → Trình duyệt xuất hiện và SỐNG
  │
  ├─► Pipeline Loop
  │     → Check → Download → Render → Upload → Log → Sleep
  │     → Browser luôn mở, không đóng giữa chu kỳ
  │
  │  [Ctrl+C] hoặc lỗi fatal
  │
  └─► Cleanup: close context → close browser → save session
```

> **Quan trọng:** Browser chỉ đóng khi:
> - User nhấn `Ctrl+C`
> - Lỗi fatal crash không recover được
> - Không đóng browser giữa các chu kỳ upload (giữ session sống để tránh TikTok re-auth)

---

## 9. Upload Success Detection

Tham khảo logic từ `backup.py`, xác định upload thành công qua **3 dấu hiệu**:

### Dấu hiệu 1: URL thay đổi

```python
SUCCESS_URL_PATTERNS = [
    "tiktokstudio/content",  # TikTok Studio redirects to content page
    "/profile",              # Redirect to profile
]
if any(pattern in page.url.lower() for pattern in SUCCESS_URL_PATTERNS):
    return True
```

### Dấu hiệu 2: UI Elements theo Region

Mỗi region có selector riêng cho nút/popup xác nhận:

```python
# src/i18n/locales/vn.py
SUCCESS_SELECTORS = [
    "button:has-text('Quản lý bài đăng')",
    "button:has-text('Tải video khác lên')",
    "div:has-text('Đã đăng lên')",
]

# src/i18n/locales/en.py
SUCCESS_SELECTORS = [
    "button:has-text('Manage posts')",
    "button:has-text('Upload another video')",
    "div:has-text('Uploaded')",
]
```

### Dấu hiệu 3: Nút Đăng biến mất

Sau khi post thành công, nút "Đăng"/"Post" biến mất khỏi DOM → confirm upload OK.

### Flow

```python
async def wait_for_upload_success(page, region: str, timeout: int = 60) -> bool:
    """Poll mỗi 0.5s, tối đa {timeout}s"""
    for _ in range(timeout * 2):
        # Check URL
        if any(p in page.url.lower() for p in SUCCESS_URL_PATTERNS):
            return True
        # Check UI selectors (region-specific)
        for selector in get_success_selectors(region):
            if await page.locator(selector).count() > 0:
                return True
        await asyncio.sleep(0.5)
    return False
```

---

## 10. Popup Handling

### Kiến trúc

Mỗi region có danh sách **popup dismiss selectors** riêng. Popup được xử lý tại 2 thời điểm:

1. **Sau khi upload file** (trước khi điền caption)
2. **Sau khi bấm Đăng** (popup xác nhận, cảnh báo bản quyền)

### Selector Map per Region

```python
# src/i18n/locales/vn.py
POPUP_DISMISS_SELECTORS = [
    "button:has-text('Đã hiểu')",
    "button:has-text('Bật')",
    "button:has-text('Xác nhận')",
    ".tiktok-modal__close",
    "[aria-label='Close']",
]

FORCE_POST_SELECTORS = [
    "button:has-text('Đăng ngay')",
    "button:has-text('Tiếp tục')",
]

# src/i18n/locales/en.py
POPUP_DISMISS_SELECTORS = [
    "button:has-text('Got it')",
    "button:has-text('Turn on')",
    "button:has-text('Confirm')",
    ".tiktok-modal__close",
    "[aria-label='Close']",
]

FORCE_POST_SELECTORS = [
    "button:has-text('Post anyway')",
    "button:has-text('Post now')",
    "button:has-text('Continue')",
]
```

### Popup Handler

```python
# src/uploader/popups.py

async def dismiss_popups(page, selectors: list[str]):
    """Quét và click tất cả popup cản trở"""
    for selector in selectors:
        try:
            btn = page.locator(selector).first
            if await btn.count() > 0:
                if await btn.is_visible(timeout=1000):
                    await btn.click()
                    await asyncio.sleep(0.3)
        except Exception:
            pass
```

---

## 11. Logging & Discord Webhook

### 11.1 Pipeline Logger (`src/logger/pipeline.py`)

Mỗi bước trong pipeline được log với timestamp và metrics:

```
[TIMELINE] 2026-07-15 14:30:00 | Session: workspace_vn | Video: dQw4w9WgXcQ
  ├── [CHECK]    Channel check: 0.32s
  ├── [DOWNLOAD] Video download: 12.45s | Raw Size: 8.2 MB | Format: 1080x1920 H.264
  ├── [RENDER]   Strategy: stealth | Audio: pitch_speedshift | Duration: 2.1s
  │              Before: 8.2 MB | After: 7.8 MB | Resolution: 1080x1920
  ├── [UPLOAD]
  │   ├── [NAV]      Page load: 1.2s
  │   ├── [FILE]     File injection: 0.3s
  │   ├── [CAPTION]  Caption fill: 0.15s
  │   └── [POST]     Post wait: 4.5s
  ├── [RESULT]   SUCCESS | Total pipeline: 20.92s
  └── [SLEEP]    Next check in: 12640s (3.5h)
```

### 11.2 Discord Webhook (`src/logger/discord_webhook.py`)

Gửi log qua Discord dạng **Embed**:

```python
async def send_pipeline_log(webhook_url: str, log_data: PipelineLog):
    embed = {
        "title": f"Upload Thành Công — {log_data.video_title}",
        "color": 0x00FF00,  # Green = success, Red = fail
        "fields": [
            {"name": "Session", "value": log_data.session_name, "inline": True},
            {"name": "Video ID", "value": log_data.video_id, "inline": True},
            {"name": "Duration", "value": f"{log_data.duration}s", "inline": True},
            {"name": "📥 Download", "value": f"{log_data.download_size}MB — {log_data.download_time}s", "inline": True},
            {"name": "🎬 Render", "value": f"{log_data.render_strategy} — {log_data.render_time}s", "inline": True},
            {"name": "📤 Upload", "value": f"{log_data.upload_time}s", "inline": True},
            {"name": "⏱️ Total", "value": f"{log_data.total_time}s", "inline": True},
            {"name": "🔗 YouTube", "value": f"https://youtube.com/shorts/{log_data.video_id}", "inline": False},
        ],
        "footer": {"text": f"ttuploader • {log_data.timestamp}"},
    }
    async with aiohttp.ClientSession() as session:
        await session.post(webhook_url, json={"embeds": [embed]})
```

### Discord Webhook Format

| Trường | Nội dung |
|--------|----------|
| **Title** | Upload Thành Công / Thất Bại + tiêu đề video |
| **Color** | Xanh lá (success) / Đỏ (fail) |
| **Fields** | Session, Video ID, Duration, Download time+size, Render strategy+time, Upload time, Total time, YouTube link |
| **Footer** | Timestamp + app name |

### Log file cục bộ

```
logs/{session_name}/{YYYY-MM-DD}.log
```

Format: JSON Lines — mỗi dòng 1 JSON object chứa toàn bộ pipeline stats.

---

## 12. Downloader (`src/downloader/ytdlp.py`)

### Chức năng

- Download Short từ YouTube channel
- Archive tracking riêng cho mỗi session
- Tự động merge audio+video

### Config

```python
ydl_opts = {
    'format': 'bestvideo[height<=1080][ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best',
    'outtmpl': str(download_dir / 'raw.%(ext)s'),
    'playlistend': 1,
    'quiet': True,
    'merge_output_format': 'mp4',
    'download_archive': str(session_dir / 'download_archive.txt'),
}
```

### Flow

```
1. Nhận channel URL
2. Append /shorts nếu cần
3. yt-dlp download với archive tracking
4. Trả về path raw video hoặc None nếu không có video mới
```

---

## 13. Renderer (`src/renderer/`)

### Chiến lược FFmpeg

#### Stealth (Default)

```bash
ffmpeg -hwaccel cuda -i input.mp4 \
  -vf "hflip,crop=iw*0.97:ih*0.97:iw*0.015:ih*0.015,scale=1080:1920,eq=brightness=0.03:contrast=1.03:saturation=1.05,setpts=PTS/1.02" \
  -af "asetrate=44100*1.03,atempo=1/1.03,aresample=44100" \
  -c:v h264_nvenc -preset p4 -rc vbr -cq 23 -b:v 0 \
  -c:a aac -b:a 128k \
  -map_metadata -1 -movflags +faststart \
  output.mp4
```

#### Loop

Video play 2 lần, mỗi nửa có color grading khác nhau.

#### Transform

Stealth + text overlay + border padding.

### GPU Detect

```python
def detect_gpu_encoder() -> str:
    """Detect available GPU encoder"""
    # Thử NVENC (NVIDIA) → QuickSync (Intel) → CPU fallback
    result = subprocess.run(["ffmpeg", "-encoders"], capture_output=True, text=True)
    if "h264_nvenc" in result.stdout:
        return "h264_nvenc"
    if "h264_qsv" in result.stdout:
        return "h264_qsv"
    return "libx264"  # CPU
```

---

## 14. Multi-Language / i18n System

### Nguyên tắc

- **1 file locale cho mỗi region** trong `src/i18n/locales/`
- Mỗi file export dict chứa: UI text, selectors, button labels
- Load locale dựa trên `TIKTOK_REGION` khi session start

### Locale Structure

```python
# src/i18n/locales/vn.py
LOCALE = {
    "browser_locale": "vi-VN",
    "upload_button_selectors": [
        "[data-e2e='select_video_button']",
        "button:has-text('Chọn video')",
        "button:has-text('Tải tập tin lên')",
    ],
    "post_button_selectors": [
        "button[data-e2e='post_video_button']",
        "button:has-text('Đăng')",
    ],
    "popup_dismiss_selectors": [...],
    "success_selectors": [...],
    "force_post_selectors": [...],
    "caption_editor_selectors": [
        "div[contenteditable='true']",
        ".public-DraftEditor-content",
    ],
}
```

### Usage

```python
# src/i18n/base.py
from .locales import vn, en, jp, kr, br, it, fr, de, es

LOCALE_MAP = {
    "VN": vn.LOCALE,
    "US": en.LOCALE,
    "JP": jp.LOCALE,
    "KR": kr.LOCALE,
    "BR": br.LOCALE,
    "IT": it.LOCALE,
    "FR": fr.LOCALE,
    "DE": de.LOCALE,
    "ES": es.LOCALE,
}

def get_locale(region: str) -> dict:
    return LOCALE_MAP.get(region.upper(), en.LOCALE)
```

---

## 15. Implementation Order (Thứ tự triển khai)

| Phase | Module | Priority |
|-------|--------|----------|
| **Phase 1** | `config/`, `cli/`, `storage/` — foundation | 🔴 P0 |
| **Phase 2** | `logger/` — logging framework + Discord | 🔴 P0 |
| **Phase 3** | `youtube/` — API check | 🔴 P0 |
| **Phase 4** | `downloader/` — yt-dlp | 🔴 P0 |
| **Phase 5** | `renderer/` — FFmpeg strategies | 🟠 P1 |
| **Phase 6** | `uploader/` — Phantomwright upload flow | 🔴 P0 |
| **Phase 7** | `i18n/` — Multi-language selectors | 🟠 P1 |
| **Phase 8** | `main.py` — Orchestration + Loop | 🔴 P0 |
| **Phase 9** | Testing + Edge cases | 🟡 P2 |

---

## 16. Ghi chú Kỹ thuật

- **Python 3.11.9** (khớp `.python-version`)
- **Virtual env:** `runtime/` (gitignored)
- **Data per session:** Mỗi session có `uploaded.txt` riêng → không cross-contamination
- **Download archive:** `download_archive.txt` cũng lưu trong session dir
- **Thread safety:** yt-dlp và FFmpeg chạy trong `loop.run_in_executor()` (thread pool)
- **Error recovery:** Crash ở bất kỳ bước nào → log lỗi → Discord notify → sleep → retry chu kỳ sau
- **Browser stays alive:** Chỉ đóng khi session kết thúc (Ctrl+C hoặc crash fatal)
