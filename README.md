<div align="center">
  <h1>🎬 ttuploader</h1>
  <h3><strong>Auto-upload YouTube Shorts → TikTok with Anti-Detection</strong></h3>

  <p>
    <img src="https://img.shields.io/badge/Python-3.11.9-blue.svg" alt="Python 3.11.9">
    <img src="https://img.shields.io/badge/Browser-Phantomwright-8A2BE2.svg" alt="Phantomwright">
    <img src="https://img.shields.io/badge/Download-yt--dlp-red.svg" alt="yt-dlp">
    <img src="https://img.shields.io/badge/Render-FFmpeg%20(NVENC)-green.svg" alt="FFmpeg NVENC">
    <img src="https://img.shields.io/badge/API-YouTube%20Data%20v3-FF0000.svg" alt="YouTube API">
    <img src="https://img.shields.io/badge/Anti--Detection-17%20Evasions-success.svg" alt="17 Evasions">
    <img src="https://img.shields.io/badge/i18n-9%20Languages-orange.svg" alt="9 Languages">
    <img src="https://img.shields.io/badge/Platform-Windows-0078D6.svg" alt="Windows">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License">
  </p>

  <p>A CLI platform that automatically finds the latest YouTube Shorts from any channel, downloads them, applies multi-layer FFmpeg rendering to bypass TikTok's duplicate detection, and uploads via Phantomwright stealth browser with proxy support and anti-detection fingerprint evasion.</p>

  <p>
    <a href="#features">Features</a> •
    <a href="#pipeline">Pipeline</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#usage">Usage</a> •
    <a href="#configuration">Configuration</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#project-structure">Project Structure</a> •
    <a href="#anti-detection">Anti-Detection</a>
  </p>

  <br/>

  **🌐 Language:** &nbsp; [English](#english) &nbsp;|&nbsp; [Tiếng Việt](#tiếng-việt) &nbsp;|&nbsp; [Español](#español)
</div>

---

<div id="english">

## ✨ Features

| Feature | Description |
| ------- | ----------- |
| **🔍 Smart Discovery** | YouTube Data API v3 checks for new Shorts on your target channel. Configurable duration filters to skip non-Short content. |
| **📥 Auto Download** | yt-dlp downloads the latest Short with optimal format selection. Built-in cookie support for authenticated YouTube access. |
| **🎬 Multi-Strategy Render** | 3 FFmpeg rendering tiers (Stealth / Loop / Transform) with GPU acceleration (NVENC) and CPU fallback. |
| **🔐 Audio Manipulation** | 7 audio strategies to break audio fingerprinting: pitch+speed shift, enhanced pitch, re-encode, audio mix, full replace, strip. |
| **📤 Stealth Upload** | Phantomwright (Playwright fork) with **17 fingerprint evasions** uploads to TikTok Studio. Proxy support with authentication. |
| **🌍 9-Region i18n** | Full locale system covering US, VN, JP, KR, BR, IT, FR, DE, ES — every UI selector translated + English fallback. |
| **📊 Discord Webhook** | Real-time pipeline telemetry sent as rich Discord Embeds: download size, render time, upload status, total pipeline duration. |
| **💾 Per-Session Storage** | Each workspace stores its own `uploaded.txt` and `download_archive.txt` — run multiple accounts in parallel without cross-contamination. |
| **🛡️ Anti-Detection** | Residential proxy + 17 browser fingerprint evasions + resource blocking + human-like interaction simulation. |
| **🔧 CLI First** | `python main.py --session workspace_vn --env .env --once` — everything controlled from the terminal. |

## 🔄 Pipeline

```mermaid
flowchart LR
    A["🔍 CHECK
    YouTube API v3"] --> B["📥 DOWNLOAD
    yt-dlp"]
    B --> C["🎬 RENDER
    FFmpeg + NVENC"]
    C --> D["📤 UPLOAD
    Phantomwright"]

    subgraph Anti-Detection
        E["Stealth Engine
        17 Evasions"]
        F["Residential Proxy"]
        G["Resource Blocker"]
    end

    D -.-> E
    D -.-> F
    D -.-> G
```

### Pipeline Sequence

```mermaid
sequenceDiagram
    participant CLI as CLI (main.py)
    participant YT as YouTube API v3
    participant DL as yt-dlp
    participant FF as FFmpeg Renderer
    participant PW as Phantomwright
    participant TK as TikTok Studio
    participant DC as Discord

    CLI->>YT: get_latest_shorts(channel)
    YT-->>CLI: [video_id, title, duration]

    alt Already uploaded
        CLI->>CLI: skip → sleep
    else New video
        CLI->>DL: download(url, cookies)
        DL-->>CLI: raw.mp4

        CLI->>FF: render(strategy=stealth)
        FF-->>CLI: processed.mp4

        CLI->>PW: navigate to upload page
        PW->>TK: cookie injection + stealth
        CLI->>PW: inject file → caption → post
        PW->>TK: upload + publish
        TK-->>PW: success / fail

        CLI->>CLI: save video_id → uploaded.txt
        CLI->>DC: send pipeline stats embed
    end

    CLI->>CLI: sleep(random 30-60 min)
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11.9** — Check with `python --version`
- **FFmpeg** — Required for video rendering. Install via `winget install ffmpeg` or from [ffmpeg.org](https://ffmpeg.org)
- **Google API Key** — [YouTube Data API v3](https://console.cloud.google.com/apis/library/youtube.googleapis.com) (free tier: 10,000 units/day)
- **TikTok Account** — With cookies exported (see below)
- **Proxy** (recommended) — Residential/mobile, SOCKS5 or HTTP

### Installation

```bash
# 1. Clone
git clone https://github.com/YOUR_USER/ttuploader.git
cd ttuploader

# 2. Create virtual environment
python -m venv runtime
runtime\Scripts\Activate.ps1   # Windows
# source runtime/bin/activate  # Linux/macOS

# 3. Install dependencies
pip install -r requirements.txt
phantomwright_driver install chromium

# 4. Copy and fill .env
cp .env.example .env
```

### Cookie Setup

**YouTube cookies** (for yt-dlp downloads):
1. Install "Get cookies.txt LOCALLY" Chrome extension
2. Go to `youtube.com` (logged in)
3. Export as JSON → save as `youtube_cookie.json` in project root

**TikTok cookies** (for Phantomwright upload):
1. Install "EditThisCookie" Chrome extension
2. Go to `tiktok.com` (logged in)
3. Export as JSON → save as `tiktok_cookies.json` in project root

### First Run

```bash
# Single test run
python main.py --session test --env .env --once

# Production loop
python main.py --session workspace_vn --env .env
```

## 📖 Usage

### CLI Commands

```bash
# Basic run with specific env and session
python main.py --session <name> --env <env_file>

# Headless mode (no browser window)
python main.py --session test --env .env --headless

# Run once and exit
python main.py --session test --env .env --once
```

### CLI Arguments

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--session` | Yes | — | Session name → creates `data/sessions/{name}/` |
| `--env` | No | `.env` | Path to environment file |
| `--headless` | No | `false` | Run browser without GUI window |
| `--once` | No | `false` | Run pipeline once and exit |
| `--interval` | No | (from .env) | Override check interval in seconds |

### Session Management

Each session is isolated:

```
data/sessions/{session_name}/
├── uploaded.txt          # List of uploaded YouTube video IDs
├── download_archive.txt  # yt-dlp archive (prevents re-download)
└── session.json          # Runtime state (counts, timestamps)
```

To reset a session (start fresh): delete the `uploaded.txt` and `download_archive.txt` files.

## ⚙️ Configuration

All configuration is in `.env`. See `.env.example` for the template.

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `GOOGLE_API_KEY` | — | YouTube Data API v3 key |
| `CHANNEL_ID` | — | YouTube channel URL or ID |
| `YT_COOKIE_FILE` | — | Path to YouTube cookies JSON file |
| `TIKTOK_COOKIE_FILE` | `tiktok_cookies.json` | Path to TikTok cookies JSON file |
| `TIKTOK_REGION` | `US` | TikTok account region (US/JP/KR/VN/BR/IT/FR/DE/ES) |
| `PROXY` | — | Proxy URL (`http://user:pass@host:port`) |
| `RENDER_STRATEGY` | `stealth` | `none` / `stealth` / `loop` / `transform` |
| `AUDIO_RENDER_STRATEGY` | `pitch_speedshift` | `none` / `pitch_speedshift` / `enhanced_pitch` / `re_encode` / `audio_mix` / `full_replace` / `no_sound` |
| `SKIP_VIDEO_IF_DURATION_MORE_THAN` | `300` | Skip videos longer than this (seconds) |
| `SKIP_VIDEO_IF_DURATION_LESS_THAN` | `0` | Skip videos shorter than this (seconds) |
| `MINIMUM_CHECK_INTERVAL` | `1800` | Min seconds between channel checks |
| `MAXIMUM_CHECK_INTERVAL` | `3600` | Max seconds between channel checks |
| `DISCORD_WEBHOOK_URL` | — | Discord webhook for notifications |
| `FALLBACK_CAPTION` | — | Default TikTok caption |
| `FALLBACK_HASHTAGS` | `#viral #trending...` | Default TikTok hashtags |

### Region → Language Mapping

| Region | Language | Browser Locale | TikTok UI Language |
|--------|----------|----------------|-------------------|
| `US` | English | `en-US` | English |
| `VN` | Tiếng Việt | `vi-VN` | Vietnamese |
| `JP` | 日本語 | `ja-JP` | Japanese |
| `KR` | 한국어 | `ko-KR` | Korean |
| `BR` | Português | `pt-BR` | Portuguese |
| `IT` | Italiano | `it-IT` | Italian |
| `FR` | Français | `fr-FR` | French |
| `DE` | Deutsch | `de-DE` | German |
| `ES` | Español | `es-ES` | Spanish |

### Render Strategies

| Strategy | Description | Speed (30s video) |
|----------|-------------|-------------------|
| `none` | No rendering, raw upload | <1s |
| `stealth` | hflip + 3% crop + color shift + 2% speed + audio shift + noise | ~3s (GPU) |
| `loop` | Video plays 2x with different color grading per half | ~6s (GPU) |
| `transform` | Stealth + unsharp mask + heavy noise + 4% crop | ~5s (GPU) |

## 🏗️ Architecture

### Project Structure

```
ttuploader/
├── main.py                          # CLI entry point + orchestration loop
├── requirements.txt                 # Python dependencies
├── src/
│   ├── config/settings.py           # .env loader with multi-line support
│   ├── cli/parser.py                # argparse CLI setup
│   ├── storage/session.py           # Per-session state + uploaded.txt tracking
│   ├── youtube/api.py               # YouTube Data API v3 wrapper
│   ├── downloader/ytdlp.py          # yt-dlp wrapper + JSON→Netscape cookie converter
│   ├── renderer/
│   │   ├── strategies.py            # Stealth/Loop/Transform FFmpeg strategies
│   │   └── runner.py                # Strategy dispatcher + GPU detection
│   ├── uploader/
│   │   ├── browser.py               # Phantomwright lifecycle + stealth + proxy
│   │   ├── upload.py                # TikTok upload flow (navigate→file→caption→post)
│   │   └── popups.py                # Multi-language popup dismiss handlers
│   ├── logger/
│   │   ├── pipeline.py              # Pipeline timing + structured logging
│   │   └── discord_webhook.py       # Discord embed sender (startup/upload/shutdown)
│   └── i18n/
│       ├── base.py                  # Locale loader with English fallback merging
│       └── locales/                 # 9 locale files (en/vn/jp/kr/br/it/fr/de/es)
├── data/sessions/{name}/            # Session data (gitignored)
├── logs/{session_name}/             # JSON Lines log files (gitignored)
└── downloads/{session_name}/        # Temp video workspace (gitignored)
```

## 🛡️ Anti-Detection

### Browser Evasion Stack

| Layer | Implementation | Detail |
|-------|---------------|--------|
| **Engine** | Phantomwright | Patched Playwright — `navigator.webdriver` hidden at browser level |
| **Evasions (17)** | `phantomwright.stealth.Stealth` | `chrome_runtime`, `navigator_*`, `webgl`, `iframe`, `media_codecs`, `hairline`, `sec_ch_ua` — all enabled |
| **Browser Args** | Chromium flags | `--disable-blink-features=AutomationControlled` — removes automation markers |
| **Proxy** | Residential | 1 account = 1 proxy. SOCKS5/HTTP with username+password auth |
| **Cookies** | Playwright native | Full TikTok session injection with proper `sameSite` handling |
| **Resource Blocker** | Route interceptor | Blocks `image`/`media` resources — reduces fingerprint surface |
| **Viewport** | 1280×800 | Standard desktop dimensions, matches region locale |
| **File Picker** | JS override | `window.showOpenFilePicker` disabled — no native dialogs |

### TikTok Detection Layers Defeated

| TikTok Layer | Countermeasure |
|-------------|----------------|
| Cryptographic Hash (MD5/SHA) | ANY re-encode bypasses |
| Perceptual Hash (pHash) | hflip + 3% crop + color shift + 2% speed |
| Computer Vision / AI | rotate 0.005° + noise + unsharp mask |
| Audio Fingerprint | Pitch shift ±7% + speed shift + re-encode |
| Metadata (EXIF/XMP) | `-map_metadata -1` + `-map_chapters -1` |
| Browser Fingerprint | 17 evasion engine + residential proxy |

## 📊 Pipeline Logging

### Console Output

```
[TIMELINE] 2026-07-15T19:30:00 | Session: test | Video: dQw4w9WgXcQ
  ├── [CHECK]    Channel check: 0.32s
  ├── [DOWNLOAD] Video download: 12.45s | Raw Size: 8.2 MB
  ├── [RENDER]   Strategy: stealth | Duration: 2.1s
  │              Before: 8.2 MB | After: 7.8 MB
  ├── [UPLOAD]
  │   ├── [NAV]      Page load: 1.2s
  │   ├── [FILE]     File injection: 0.3s
  │   ├── [CAPTION]  Caption fill: 0.15s
  │   └── [POST]     Post wait: 4.5s
  ├── [RESULT]   SUCCESS | Total pipeline: 20.92s
```

### Discord Embed

Each upload/dowload/render result is sent as a formatted Discord embed with color-coded status (green = success, red = fail), including file sizes, timing breakdown, and YouTube link.

## 🧪 Render Performance

Measured on NVIDIA RTX GPU with `h264_nvenc` encoder:

| Strategy | 15s Video | 30s Video | 60s Video |
|----------|-----------|-----------|-----------|
| `stealth` | ~1.5s | ~3s | ~6s |
| `loop` | ~4s | ~6s | ~10s |
| `transform` | ~3s | ~5s | ~8s |

GPU encoder automatically detected. Falls back to CPU (`libx264`) if no GPU available.

---

</div>

---

<div id="tiếng-việt">

## ✨ Tính Năng

| Tính năng | Mô tả |
| --------- | ----- |
| **🔍 Phát hiện thông minh** | YouTube Data API v3 quét Short mới nhất từ kênh mục tiêu. Bộ lọc thời lượng tùy chỉnh. |
| **📥 Tự động tải** | yt-dlp tải Short với format tối ưu. Hỗ trợ cookie để xác thực YouTube. |
| **🎬 Render đa chiến lược** | 3 tầng FFmpeg (Stealth / Loop / Transform) với GPU NVENC và fallback CPU. |
| **🔐 Xử lý âm thanh** | 7 chiến lược audio để phá fingerprint: pitch+speed shift, enhanced pitch, re-encode, audio mix, full replace, strip. |
| **📤 Upload ẩn** | Phantomwright với **17 lớp fingerprint evasion** upload lên TikTok Studio. Hỗ trợ proxy có xác thực. |
| **🌍 9 ngôn ngữ** | Hệ thống locale đầy đủ: US, VN, JP, KR, BR, IT, FR, DE, ES — mọi UI selector được dịch + fallback tiếng Anh. |
| **📊 Discord Webhook** | Telemetry realtime gửi qua Discord Embed: dung lượng tải, thời gian render, trạng thái upload, tổng pipeline. |
| **💾 Lưu trữ theo session** | Mỗi workspace có `uploaded.txt` và `download_archive.txt` riêng — chạy nhiều tài khoản song song không xung đột. |
| **🛡️ Chống phát hiện** | Proxy residential + 17 lớp fingerprint evasion + chặn resource + mô phỏng hành vi người dùng. |
| **🔧 CLI** | `python main.py --session workspace_vn --env .env --once` — tất cả điều khiển từ terminal. |

## 🚀 Cài Đặt Nhanh

### Yêu cầu

- **Python 3.11.9**
- **FFmpeg** — `winget install ffmpeg`
- **Google API Key** — [YouTube Data API v3](https://console.cloud.google.com/apis/library/youtube.googleapis.com)
- **Tài khoản TikTok** — Đã export cookie

### Cài đặt

```bash
git clone https://github.com/YOUR_USER/ttuploader.git
cd ttuploader
python -m venv runtime
runtime\Scripts\Activate.ps1
pip install -r requirements.txt
phantomwright_driver install chromium
cp .env.example .env
```

### Lấy Cookie

**YouTube:** Cài extension "Get cookies.txt LOCALLY" → vào youtube.com → Export JSON → lưu `youtube_cookie.json`

**TikTok:** Cài "EditThisCookie" → vào tiktok.com → Export JSON → lưu `tiktok_cookies.json`

### Chạy

```bash
python main.py --session test --env .env --once      # Test 1 lần
python main.py --session workspace_vn --env .env      # Chạy liên tục
```

## ⚙️ Cấu Hình

| Biến | Mặc định | Mô tả |
| -------- | ------- | ----------- |
| `GOOGLE_API_KEY` | — | Khóa YouTube Data API v3 |
| `CHANNEL_ID` | — | URL hoặc ID kênh YouTube |
| `YT_COOKIE_FILE` | — | Đường dẫn file cookie YouTube JSON |
| `TIKTOK_COOKIE_FILE` | `tiktok_cookies.json` | Đường dẫn file cookie TikTok JSON |
| `TIKTOK_REGION` | `US` | Region tài khoản TikTok |
| `PROXY` | — | URL proxy (`http://user:pass@host:port`) |
| `RENDER_STRATEGY` | `stealth` | Chiến lược render |
| `AUDIO_RENDER_STRATEGY` | `pitch_speedshift` | Chiến lược xử lý audio |
| `DISCORD_WEBHOOK_URL` | — | Webhook Discord thông báo |
| `MINIMUM_CHECK_INTERVAL` | `1800` | Thời gian check tối thiểu (giây) |
| `MAXIMUM_CHECK_INTERVAL` | `3600` | Thời gian check tối đa (giây) |

## 🛡️ Chống Phát Hiện

| Lớp TikTok | Biện pháp đối phó |
|-----------|-------------------|
| Hash mật mã (MD5/SHA) | BẤT KỲ re-encode nào cũng bypass |
| Hash tri giác (pHash) | hflip + crop 3% + đổi màu + tăng tốc 2% |
| Computer Vision / AI | xoay 0.005° + noise + unsharp mask |
| Audio Fingerprint | Pitch shift ±7% + speed shift + re-encode |
| Metadata (EXIF/XMP) | `-map_metadata -1` + `-map_chapters -1` |
| Vân tay trình duyệt | 17 evasion engine + proxy residential |

---

</div>

---

<div id="español">

## ✨ Características

| Característica | Descripción |
| -------------- | ----------- |
| **🔍 Detección inteligente** | YouTube Data API v3 busca nuevos Shorts en tu canal objetivo. Filtros de duración configurables. |
| **📥 Descarga automática** | yt-dlp descarga el último Short con formato óptimo. Soporte de cookies para YouTube autenticado. |
| **🎬 Render multi-estrategia** | 3 niveles FFmpeg (Stealth/Loop/Transform) con aceleración GPU NVENC y fallback CPU. |
| **🔐 Manipulación de audio** | 7 estrategias para romper fingerprinting de audio: pitch+speed, enhanced pitch, re-encode, mix, replace, strip. |
| **📤 Subida sigilosa** | Phantomwright con **17 evasiones de huella digital** sube a TikTok Studio. Proxy con autenticación. |
| **🌍 9 idiomas** | Sistema locale completo: US, VN, JP, KR, BR, IT, FR, DE, ES — cada selector traducido + fallback inglés. |
| **📊 Discord Webhook** | Telemetría en tiempo real como Embeds de Discord: tamaño de descarga, tiempo de render, estado de subida. |
| **💾 Almacenamiento por sesión** | Cada workspace tiene su propio `uploaded.txt` y `download_archive.txt` — ejecuta múltiples cuentas en paralelo. |
| **🛡️ Anti-detección** | Proxy residencial + 17 evasiones + bloqueo de recursos + simulación de comportamiento humano. |
| **🔧 CLI** | `python main.py --session test --env .env --once` — todo controlado desde la terminal. |

## 🚀 Inicio Rápido

```bash
git clone https://github.com/YOUR_USER/ttuploader.git
cd ttuploader
python -m venv runtime
runtime\Scripts\Activate.ps1        # Windows
pip install -r requirements.txt
phantomwright_driver install chromium
cp .env.example .env
# Configurar .env con tus claves API y cookies
python main.py --session test --env .env --once
```

## ⚙️ Configuración

| Variable | Predeterminado | Descripción |
| -------- | -------------- | ----------- |
| `GOOGLE_API_KEY` | — | Clave de YouTube Data API v3 |
| `CHANNEL_ID` | — | URL o ID del canal de YouTube |
| `YT_COOKIE_FILE` | — | Ruta al archivo JSON de cookies de YouTube |
| `TIKTOK_COOKIE_FILE` | `tiktok_cookies.json` | Ruta al archivo JSON de cookies de TikTok |
| `TIKTOK_REGION` | `US` | Región de la cuenta TikTok |
| `PROXY` | — | URL del proxy (`http://user:pass@host:port`) |
| `RENDER_STRATEGY` | `stealth` | Estrategia de renderizado |
| `DISCORD_WEBHOOK_URL` | — | Webhook de Discord para notificaciones |

## 🛡️ Anti-Detección

| Capa de TikTok | Contramedida |
|---------------|-------------|
| Hash criptográfico (MD5/SHA) | CUALQUIER re-codificación lo evita |
| Hash perceptual (pHash) | hflip + crop 3% + cambio de color + velocidad 2% |
| Visión artificial / IA | rotación 0.005° + ruido + máscara unsharp |
| Huella de audio | Pitch shift ±7% + speed shift + re-codificación |
| Metadatos (EXIF/XMP) | `-map_metadata -1` + `-map_chapters -1` |
| Huella del navegador | 17 evasiones + proxy residencial |

---

</div>

---

## 📁 Project Structure

```
ttuploader/
├── main.py                          # CLI entry point + orchestration loop
├── requirements.txt                 # Python dependencies
├── src/
│   ├── config/settings.py           # .env loader with multi-line value support
│   ├── cli/parser.py                # argparse CLI setup
│   ├── storage/session.py           # Per-session state + uploaded.txt tracking
│   ├── youtube/api.py               # YouTube Data API v3 wrapper
│   ├── downloader/ytdlp.py          # yt-dlp wrapper + JSON→Netscape cookie converter
│   ├── renderer/
│   │   ├── strategies.py            # Stealth / Loop / Transform FFmpeg strategies
│   │   └── runner.py                # Strategy dispatcher + GPU auto-detection
│   ├── uploader/
│   │   ├── browser.py               # Phantomwright lifecycle + stealth engine + proxy
│   │   ├── upload.py                # TikTok upload flow (navigate → file → caption → post)
│   │   └── popups.py                # Multi-language popup dismiss handlers
│   ├── logger/
│   │   ├── pipeline.py              # Pipeline timing + structured JSON Lines logging
│   │   └── discord_webhook.py       # Discord embed sender (startup / upload / shutdown)
│   └── i18n/
│       ├── base.py                  # Locale loader with English fallback auto-merge
│       └── locales/                 # 9 locale files: en, vn, jp, kr, br, it, fr, de, es
├── data/sessions/{name}/            # Session data (gitignored)
├── logs/{session_name}/             # JSON Lines log files (gitignored)
└── downloads/{session_name}/        # Temp video workspace (gitignored)
```

## 🔧 Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11.9 |
| Browser Automation | Phantomwright 0.2.0 (Playwright fork + stealth) |
| Video Download | yt-dlp |
| Video Render | FFmpeg (h264_nvenc / libx264) |
| Channel Discovery | YouTube Data API v3 (google-api-python-client) |
| Config | python-dotenv |
| Logging | aiohttp (Discord Webhook) |
| Image Processing | OpenCV + NumPy (captcha solver fallback) |

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

</div>

<br/>
<div align="center">
  <sub>...</sub>
</div>
