import asyncio
import base64
import json
import os
import sys
import random
import tempfile
import glob

import cv2
import numpy as np

# ─── Env (DOCKER READY) ──────────────────────────────────────────────────────
WORKSPACE_ID    = os.environ.get("WORKSPACE_ID", "unknown")
PROXY_URL       = os.environ.get("PROXY_URL", "")
COOKIE_JSON_B64 = os.environ.get("COOKIE_JSON_B64", "")
YT_SOURCES      = os.environ.get("YT_SOURCES", "")

DOWNLOADS_DIR   = "/app/downloads"
TEMP_VIDEO_TMPL = os.path.join(DOWNLOADS_DIR, "temp")   

SLEEP_BETWEEN_CHANNELS = 5   # 5 phút giữa các kênh
SLEEP_CYCLE            = 15    # 1 phút sau mỗi chu kỳ

# ─── Garbage Collection ──────────────────────────────────────────────────────
def cleanup_workspace():
    _log("\n[*] 🧹 Đang dọn dẹp Workspace (Garbage Collection)...")
    try:
        files = glob.glob(os.path.join(DOWNLOADS_DIR, "*"))
        count = 0
        for f in files:
            if os.path.isfile(f):
                try:
                    os.remove(f)
                    count += 1
                except Exception: pass
        _log(f"[✓] Đã dọn sạch {count} file rác.")
    except Exception as e:
        _log(f"[!] Lỗi dọn rác: {e}")

# ─── Cookie decoder (Base64 Restored) ────────────────────────────────────────
def _decode_cookie() -> list:
    if not COOKIE_JSON_B64: return []
    VALID_SAME_SITE = {"Strict", "Lax", "None"}
    PLAYWRIGHT_KEYS = {"name", "value", "domain", "path", "expires", "httpOnly", "secure", "sameSite"}
    try:
        raw  = base64.b64decode(COOKIE_JSON_B64).decode("utf-8")
        data = json.loads(raw)
        if isinstance(data, list):
            normalized = []
            for cookie in data:
                if not isinstance(cookie, dict): continue
                if cookie.get("sameSite") not in VALID_SAME_SITE:
                    cookie["sameSite"] = "None"
                cleaned = {k: v for k, v in cookie.items() if k in PLAYWRIGHT_KEYS}
                if "name" in cleaned and "value" in cleaned:
                    normalized.append(cleaned)
            return normalized
        return []
    except Exception: return []

# ─── Logging & Path ──────────────────────────────────────────────────────────
def _parse_yt_sources(raw: str) -> list:
    return [u.strip() for u in raw.replace('\n', ',').split(',') if u.strip()]

def _log(msg: str):
    print(msg, flush=True)

def generate_bezier_path(start_x, start_y, end_x, end_y, steps=60):
    mid_x, mid_y = (start_x + end_x) / 2, (start_y + end_y) / 2
    cp1_x, cp1_y = mid_x + random.uniform(-30, 30), mid_y + random.uniform(-20, 20)
    cp2_x, cp2_y = mid_x + random.uniform(-30, 30), mid_y + random.uniform(-20, 20)
    points = []
    for i in range(steps + 1):
        t_linear = i / steps
        t = t_linear * t_linear * (3 - 2 * t_linear)
        u = 1 - t
        x = u**3*start_x + 3*u**2*t*cp1_x + 3*u*t**2*cp2_x + t**3*end_x
        y = u**3*start_y + 3*u**2*t*cp1_y + 3*u*t**2*cp2_y + t**3*end_y
        jitter = 4 * t_linear * (1 - t_linear)
        points.append((x + random.gauss(0, 1.2) * jitter, y + random.gauss(0, 0.8) * jitter))
    return points

# ─── Giải Captcha ────────────────────────────────────────────────────────────
# ─── Giải Captcha ────────────────────────────────────────────────────────────
async def solve_tiktok_captcha(page) -> bool:
    CAPTCHA_SELECTORS = [".captcha_verify_container", "#captcha-verify-image", ".cap-flex", "[class*='captcha']"]
    
    # 1. Check xem có captcha không (Fix lỗi async generator)
    captcha_found = False
    for sel in CAPTCHA_SELECTORS:
        if await page.locator(sel).count() > 0:
            captcha_found = True
            break
            
    if not captcha_found:
        return True # Không có captcha -> An toàn đi tiếp

    _log("[*] Phát hiện Captcha Slider, đang giải...")
    try:
        bg_elem = page.locator("#captcha-verify-image").first
        piece_elem = page.locator(".cap-absolute").first
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f: bg_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f: piece_path = f.name
        await bg_elem.screenshot(path=bg_path)
        await piece_elem.screenshot(path=piece_path)

        bg_img, piece_img = cv2.imread(bg_path, cv2.IMREAD_COLOR), cv2.imread(piece_path, cv2.IMREAD_COLOR)
        bg_edges = cv2.Canny(cv2.cvtColor(bg_img, cv2.COLOR_BGR2GRAY), 50, 150)
        piece_edges = cv2.Canny(cv2.cvtColor(piece_img, cv2.COLOR_BGR2GRAY), 50, 150)
        
        _, _, _, max_loc = cv2.minMaxLoc(cv2.matchTemplate(bg_edges, piece_edges, cv2.TM_CCOEFF_NORMED))
        target_x = max_loc[0]

        for p in (bg_path, piece_path):
            try: os.remove(p)
            except Exception: pass

        slider = page.locator(".secsdk-captcha-drag-icon, [class*='drag'], [class*='slider']").first
        box = await slider.bounding_box()
        if not box: return False

        sx, sy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        await page.mouse.move(sx, sy)
        await page.mouse.down()
        for (px, py) in generate_bezier_path(sx, sy, sx + target_x, sy + random.uniform(-2, 2), steps=55):
            await page.mouse.move(px, py)
            await asyncio.sleep(random.uniform(0.003, 0.018))
        await page.mouse.up()
        await page.wait_for_timeout(2500)
        
        # 2. Check lại xem captcha đã biến mất chưa (Fix lỗi async generator)
        still_has_captcha = False
        for s in CAPTCHA_SELECTORS:
            if await page.locator(s).count() > 0:
                still_has_captcha = True
                break
                
        if not still_has_captcha:
            _log("[✓] Captcha giải thành công!")
            return True
        return False
    except Exception: return False

# ─── YouTube Downloader (Merged Audio/Video Restored) ────────────────────────
# ─── YouTube Downloader (Anti-Duplicate & Auto-Archive) ──────────────────────
async def download_video(channel_url: str, proxy_url: str):
    import yt_dlp
    normalized_url = channel_url.rstrip('/')
    if '@' in normalized_url and not any(s in normalized_url for s in ['/shorts', '/videos', '/live']):
        normalized_url += '/shorts'

    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    
    # VŨ KHÍ CHỐNG TRÙNG LẶP: Lưu file archive ở /app (bên ngoài thư mục downloads) 
    # để không bị hàm cleanup_workspace() xóa nhầm.
    archive_file = "/app/downloaded_archive.txt"

    ydl_opts = {
        'format': 'bestvideo[height<=720][ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best',
        'outtmpl': TEMP_VIDEO_TMPL + '.%(ext)s',
        'playlistend': 1,  # Quét sâu 5 video mới nhất
        'quiet': False, 
        'no_warnings': False, 
        'merge_output_format': 'mp4',
        'download_archive': archive_file, # Lệnh kích hoạt bộ nhớ
    }
    try:
        _log(f"[*] Đang quét tối đa 1 video mới nhất từ: {normalized_url}")
        loop = asyncio.get_event_loop()
        
        # yt-dlp sẽ tự động bỏ qua nếu video đã nằm trong archive
        await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).download([normalized_url]))
        
        # Kiểm tra xem có video temp nào thực sự được tải về không
        found = glob.glob(os.path.join(DOWNLOADS_DIR, 'temp.*'))
        if found: 
            return found[0]
        
        _log("[*] Không phát hiện video mới (hoặc đã Up hết). Bỏ qua kênh này.")
        return None
    except Exception as exc:
        _log(f"[✗] Lỗi yt-dlp: {exc}")
        return None

CAPTION_TEMPLATE = os.environ.get("CAPTION_TEMPLATE", "")
CUSTOM_HASHTAGS  = os.environ.get("CUSTOM_HASHTAGS", "#viral, #trending")

def _parse_hashtags(raw: str) -> list:
    return [h.strip() for h in raw.replace('\n', ',').split(',') if h.strip()]

async def process_video_metadata(input_path: str) -> str:
    import subprocess
    import time
    import random
    import math
    import os

    start_render = time.time()
    out_path = input_path.replace("temp.", "processed.")
    
    # 1. Trích xuất thông số Duration thông qua ffprobe
    probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_path]
    try:
        duration = float(subprocess.check_output(probe_cmd).decode("utf-8").strip())
    except Exception:
        duration = 15.0 
        
    _log(f"[*] Thu thập dữ liệu Metadata: Thời lượng gốc = {duration:.2f}s")

    if duration < 61.0:
        _log("[*] Detect: Thời lượng < 61s. Kích hoạt Concat Demuxer để lặp luồng Bitstream...")
        # Tính toán hệ số lặp (Vd: Video 15s cần lặp 5 lần để vượt 61.5s)
        loop_count = math.ceil(61.5 / duration)
        list_file = input_path + ".txt"
        
        # Mapping các đường dẫn tuyệt đối vào tệp tin chỉ mục
        abs_input_path = os.path.abspath(input_path).replace("\\", "/")
        with open(list_file, "w") as f:
            for _ in range(loop_count):
                f.write(f"file '{abs_input_path}'\n")
        
        # Thực thi việc nối tệp ở cấp độ Container, cắt ngắt tiến trình tại giây 61.5
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file,
            "-t", "61.5",            
            "-c", "copy",            
            "-map_metadata", "-1",
            out_path
        ]
    else:
        _log("[*] Detect: Thời lượng đạt chuẩn (> 61s). Kích hoạt Standard Stream Copy...")
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-c:v", "copy",
            "-c:a", "copy",
            "-map_metadata", "-1",
            out_path
        ]
        list_file = None

    # Khởi chạy FFmpeg trên phân luồng I/O độc lập
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, lambda: subprocess.run(cmd, capture_output=True))
    
    # Garbage collection cho tệp chỉ mục
    if list_file and os.path.exists(list_file):
        os.remove(list_file)
        
    render_time = time.time() - start_render
    
    if res.returncode == 0 and os.path.exists(out_path): 
        # Thực thi tiêm byte Hex vào cuối EOF nhằm phá vỡ cấu trúc mã Hash
        with open(out_path, "ab") as f:
            f.write(os.urandom(random.randint(1024, 5120)))
            
        _log(f"[✓] Tiến trình ghi đĩa và thay đổi định danh hoàn tất. ⏱️ Render: {render_time:.4f}s")
        return out_path
    
    _log(f"[!] Ngoại lệ xảy ra tại I/O Stream. Kích hoạt Fallback. ⏱️ Latency: {render_time:.4f}s")
    return input_path

async def upload_tiktok(page, video_path: str, video_title: str = "") -> bool:
    import time
    try:
        t0 = time.time()
        video_path = await process_video_metadata(video_path)
        t_render = time.time() - t0
        start_upload = time.time()
        # _log("[*] Điều hướng tới TikTok Studio Upload ...")
        t_nav_start = time.time()
        # await page.goto("https://www.tiktok.com/tiktokstudio/upload", wait_until="domcontentloaded", timeout=60_000)

        if "tiktokstudio/upload" not in page.url:
            _log("[*] Phát hiện đi lạc trang, đang điều hướng lại...")
            await page.goto("https://www.tiktok.com/tiktokstudio/upload", wait_until="domcontentloaded")
        t_nav = time.time() - t_nav_start
        # await asyncio.sleep(3)
        if "login" in page.url.lower(): 
            _log("[!] Cảnh báo: Cookie đã chết hoặc bị TikTok đá ra ngoài.")
            return False

        await page.evaluate('''() => {
            window.showOpenFilePicker = undefined;
            Object.defineProperty(window, 'showOpenFilePicker', { get: () => undefined });
        }''')

        _log("[*] Đang rình nút Upload ...")
        # t_file_start = time.time()
        # try:
        #     upload_selectors = [
        #         "[data-e2e='select_video_button']",
        #         "button:has-text('Select video')",
        #         "button:has-text('Chọn video')",
        #         "button:has-text('Tải tập tin lên')",
        #         "div:has-text('Chọn video')",
        #         "label:has-text('Chọn video')"
        #     ]
        #     upload_btn = page.locator(", ".join(upload_selectors)).first
        #     await upload_btn.wait_for(state="visible", timeout=30_000)
        # except Exception as e:
        #     error_img = os.path.join(DOWNLOADS_DIR, "error_timeout.png")
        #     await page.screenshot(path=error_img)
        #     _log(f"[!] LỖI: Không thấy nút Upload. Đã chụp ảnh màn hình lưu tại: {error_img}")
        #     _log(f"[!] NẾU DÙNG DOCKER: Hãy xem lại Cookie có bị TikTok đá ra ngoài do đổi IP Proxy không!")
        #     raise e

        # async with page.expect_file_chooser(timeout=15_000) as fc_info:
        #     await upload_btn.click(force=True, delay=200)
        
        # file_chooser = await fc_info.value
        # await file_chooser.set_files(video_path)
        # t_file = time.time() - t_file_start
        # _log(f"[✓] Nạp tệp tin vào bộ nhớ đệm thành công! (Tốn {t_file:.4f}s)")

        t_file_start = time.time()
        try:
            # 1. TÌM NÚT UPLOAD ĐỂ MỒI
            upload_btn = page.locator("[data-e2e='select_video_button'], button:has-text('Select video'), button:has-text('Chọn video')").first
            await upload_btn.wait_for(state="visible", timeout=15000)
            
            # 2. CLICK MỒI VÀ CHẶN FILE CHOOSER (Để tránh hiện cửa sổ Windows/Linux)
            async with page.expect_file_chooser() as fc_info:
                await upload_btn.click(delay=100)
            
            # 3. TIÊM FILE NGAY LẬP TỨC VÀO CHOOSER VỪA MỞ
            file_chooser = await fc_info.value
            await file_chooser.set_files(video_path)
            
            t_file = time.time() - t_file_start
            _log(f"[✓] Nạp tệp bằng kỹ thuật Priming thành công! (Tốn {t_file:.4f}s)")
        except Exception as e:
            err_path = os.path.join(DOWNLOADS_DIR, "error_priming_upload.png")
            await page.screenshot(path=err_path)
            _log(f"[!] Priming Upload THẤT BẠI. Đã chụp ảnh: {err_path} | Lỗi: {e}")
            raise e

        # _log("[*] Chờ TikTok upload file và render UI (2s)...")
        # await page.wait_for_timeout(2_000)

        _log("[*] Đang chờ UI TikTok chuyển sang form Đăng bài...")
        editor = page.locator("div[contenteditable='true'], .public-DraftEditor-content").first
        await editor.wait_for(state="visible", timeout=30_000)
        
        # 2. NHƯỢNG QUYỀN CHO ANIMATION TIKTOK (Đợi Popup Fade-in hoàn tất)
        # Lúc này Editor đã hiện, nhưng Popup có thể đang mờ dần lấp lên. Cho nó 1 giây để hiện rõ rệt.
        await asyncio.sleep(1)

        _log("[*] Quét và tiêu diệt mọi Popup cản đường...")
        popup_selectors = [
            "button:has-text('Đã hiểu')",
            "button:has-text('Bật')", 
            "button:has-text('Got it')",
            "button:has-text('Xác nhận')",
            ".tiktok-modal__close", 
            "[aria-label='Close']", 
            ".secsdk-captcha-drag-icon"
        ]
        for dismiss_sel in popup_selectors:
            try:
                btn = page.locator(dismiss_sel).first
                if await btn.count() > 0 and await btn.is_visible(timeout=1000):
                    await btn.click()
                    _log(f"[*] Đã chém rụng popup bằng selector: {dismiss_sel}")
                    # await page.wait_for_timeout(1000)
            except Exception: pass

        # _log("[*] Đang gõ Caption và Hashtag...")
        # _log(f"[*] Caption: {CAPTION_TEMPLATE}")
        # _log(f"[*] Hashtags: {CUSTOM_HASHTAGS}")
        # parsed_caption = CAPTION_TEMPLATE.strip()
        
        # # Lấy random 3 hashtag (nếu có đủ 3)
        # hashtags_list = _parse_hashtags(CUSTOM_HASHTAGS)
        # k = min(10, len(hashtags_list))
        # selected_tags = random.sample(hashtags_list, k=k) if k > 0 else []
        
        # full_cap = f"{parsed_caption} {' '.join(selected_tags)}"
        # for cap_sel in ["div[contenteditable='true']", ".public-DraftEditor-content"]:
        #     try:
        #         cap_el = page.locator(cap_sel).first
        #         if await cap_el.count() > 0:
        #             await cap_el.click()
        #             # ─── BƯỚC QUAN TRỌNG: XÓA CHỮ "PROCESSED" TỰ ĐỘNG ───
        #             # Nhấn Ctrl + A (chọn tất cả) rồi Backspace (xóa sạch)
        #             await page.keyboard.press("Control+A")
        #             await page.keyboard.press("Backspace")
        #             await asyncio.sleep(0.5) # Nghỉ xíu cho UI nó phản hồi
        #             for char in full_cap: 
        #                 await cap_el.type(char, delay=random.uniform(20, 80))
        #             break
        #     except Exception: pass

        _log("[*] Cấu trúc Caption Payload...")
        t_cap_start = time.time()
        parsed_caption = CAPTION_TEMPLATE.strip()
        hashtags_list = _parse_hashtags(CUSTOM_HASHTAGS)
        k = min(10, len(hashtags_list))
        selected_tags = random.sample(hashtags_list, k=k) if k > 0 else []
        full_cap = f"{parsed_caption} {' '.join(selected_tags)}"
        
        editor = page.locator("div[contenteditable='true'], .public-DraftEditor-content").first
        await editor.wait_for(state="visible", timeout=15000)
        await editor.fill(full_cap)
        t_cap = time.time() - t_cap_start
        _log(f"[✓] Tiêm Caption hoàn tất. (Tốn {t_cap:.4f}s)")

        # if not await solve_tiktok_captcha(page): return False

        # ── RÌNH VÀ BẤM NÚT ĐĂNG ĐẾN KHI THÀNH CÔNG ──
        _log("[*] Đang rình nút Đăng sáng lên (Chờ upload & Check bản quyền)...")
        post_selectors = [
            "button[data-e2e='post_video_button']",
            "button:has-text('Đăng')",
            "button:has-text('Post')"
        ]
        
        success_posted = False
        for i in range(150): # Thử tối đa 60 giây (30 lần x 2s)
            try:
                # 1. Quét dấu hiệu xác nhận đăng thành công từ TikTok
                is_success_ui = False
                
                # Dấu hiệu 1: TikTok tự động chuyển hướng URL sang trang Quản lý
                if "tiktokstudio/content" in page.url.lower() or "/profile" in page.url.lower():
                    is_success_ui = True
                else:
                    # Dấu hiệu 2: Các popup/toast thông báo trên giao diện cũ
                    success_signs = [
                        "button:has-text('Quản lý bài đăng')", 
                        "button:has-text('Manage posts')",
                        "button:has-text('Tải video khác lên')", 
                        "button:has-text('Upload another video')",
                        "div:has-text('Đã đăng lên')",
                        "div:has-text('Uploaded')"
                    ]
                    for s in success_signs:
                        if await page.locator(s).count() > 0 and await page.locator(s).first.is_visible():
                            is_success_ui = True
                            break
                
                if is_success_ui:
                    _log("[✓] XÁC NHẬN 100%: TikTok đã Đăng bài thành công!")
                    success_posted = True
                    break

                # 2. Nếu chưa thành công, tìm và bấm nút Đăng (Chỉ bấm khi nút sáng)
                for sel in post_selectors:
                    btn = page.locator(sel).last
                    if await btn.count() > 0 and await btn.is_visible():
                        await btn.hover()
                        await btn.click(force=True)
                        if i % 5 == 0:
                            _log("[*] Nút Đăng đã sáng! Đã click và đang chờ phản hồi...")
                        break
                        
                # 3. TIÊU DIỆT TRÙM CUỐI: Popup "Tiếp tục đăng?" -> Bấm "Đăng ngay"
                try:
                    force_post_selectors = ["button:has-text('Đăng ngay')", "button:has-text('Post anyway')", "button:has-text('Post now')"]
                    for fps in force_post_selectors:
                        force_post_btn = page.locator(fps).last
                        if await force_post_btn.count() > 0 and await force_post_btn.is_visible():
                            await force_post_btn.click(force=True)
                            _log(f"[*] Đã đập tan popup cảnh báo bằng nút: {fps}. Ép đăng luôn!")
                            t_code_execution = t_file + t_cap + t_nav 

                            _log("\n" + "="*40)
                            _log(f"📊 BÁO CÁO MICRO-TELEMETRY (Đã gạt bỏ chờ UI tĩnh):")
                            _log(f"Render : {t_render:.4f}")
                            _log(f"  - Load Trang Web:    {t_nav:.4f}s (Trễ Mạng)")
                            _log(f"  - Tiêm File Input:   {t_file:.4f}s (Code Run)")
                            _log(f"  - Tiêm Caption:      {t_cap:.4f}s (Code Run)")
                            _log("-" * 40)
                            _log(f"🔥 THỜI GIAN CODE THỰC SỰ XỬ LÝ: {t_code_execution:.4f} giây!")
                            _log(f"🔥 CHU KÌ CODE DÀNH CHO 1 VIDEO: {time.time() - start_upload:.2f} giây")
                            _log("="*40 + "\n")
                            break
                except Exception: pass
            except Exception: pass
            
            await asyncio.sleep(0.1)

        if not success_posted:
            _log("[!] CẢNH BÁO: Đã hết thời gian chờ mà video chưa được đăng.")
            error_img = os.path.join(DOWNLOADS_DIR, "error_post_failed.png")
            await page.screenshot(path=error_img)
            _log(f"[!] Đã chụp ảnh lưu tại: {error_img} để mổ tử thi.")
            return False
        return True
    except Exception as exc:
        _log(f"[✗] Lỗi upload_tiktok: {exc}")
        return False

# ─── Vòng Lặp Chính ──────────────────────────────────────────────────────────
async def run_bot():
    _log("\n" + "="*50)
    _log(f"[*] 🚀 HỆ THỐNG BOT BẮT ĐẦU KHỞI ĐỘNG...")
    _log(f"[*] 📂 WORKSPACE_ID : {WORKSPACE_ID}")
    _log(f"[*] 🎬 YT_SOURCES   : {YT_SOURCES}")
    _log(f"[*] 🍪 COOKIE_DATA  : {'[CÓ DỮ LIỆU]' if COOKIE_JSON_B64 else '[TRỐNG] !!'}")
    _log(f"[*] 📡 PROXY_URL    : {PROXY_URL}")
    _log("="*50 + "\n")


    from playwright.async_api import async_playwright
    from urllib.parse import urlparse
    
    cookies = _decode_cookie()
    channels = _parse_yt_sources(YT_SOURCES)
    
    proxy_args = {}
    if PROXY_URL:
        parsed = urlparse(PROXY_URL)
        p_dict = {"server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"}
        if parsed.username and parsed.password:
            p_dict["username"] = parsed.username
            p_dict["password"] = parsed.password
        proxy_args = {"proxy": p_dict}

    async with async_playwright() as pw:
        _log("[*] Khởi động Xvfb Chromium (Headful) ...")
        browser = await pw.chromium.launch(
            headless=False,
            args=[
                "--no-sandbox", 
                "--disable-setuid-sandbox", 
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-software-rasterizer"
            ],
            **proxy_args,
        )
        context = await browser.new_context(viewport={"width": 1280, "height": 800}, locale="vi-VN")
        if cookies: await context.add_cookies(cookies)
        page = await context.new_page()

        # --- VŨ KHÍ MỚI: BỘ LỌC TÀI NGUYÊN (NETWORK INTERCEPTOR) ---
        async def aggressive_blocker(route):
            if route.request.resource_type in ["image", "media"]:
                await route.abort()
            else:
                await route.continue_()

        await page.route("**/*", aggressive_blocker)
        # -----------------------------------------------------------

        while True:
            if not channels:
                _log("[!] ⚠️ CẢNH BÁO: Không có kênh Youtube (YT_SOURCES trống). Bot ngủ 60s chờ hệ thống bơm dữ liệu...")
                await asyncio.sleep(SLEEP_CYCLE)
                continue

            for ch in channels:
                cleanup_workspace()
                _log(f"\n[*] Đang xử lý kênh: {ch}")
                v_path = await download_video(ch, PROXY_URL)
                if v_path: 
                    success = await upload_tiktok(page, v_path)
                    if success:
                        _log("[✓] HOÀN THÀNH 1 VIDEO!")
                        await page.goto("https://www.tiktok.com/tiktokstudio/upload", wait_until="domcontentloaded")
                await asyncio.sleep(SLEEP_BETWEEN_CHANNELS)
                
            _log(f"\n[✓] Xong 1 chu kỳ quét toàn bộ kênh. Bot ngủ {SLEEP_CYCLE}s nhưng giữ trình duyệt...")
            # Trước khi ngủ, đưa page về trang upload sẵn để chu kỳ sau nổ máy là có luôn
            try:
                await page.goto("https://www.tiktok.com/tiktokstudio/upload")
            except: 
                pass
            finally:
                cleanup_workspace()

            _log(f"\n[✓] Xong chu kỳ. Bot ngủ {SLEEP_CYCLE}s ...")
            await asyncio.sleep(SLEEP_CYCLE)

async def main():
    while True:
        try: await run_bot()
        except Exception as exc:
            _log(f"[✗] Crash toàn hệ thống: {exc}")
            await asyncio.sleep(30)

if __name__ == "__main__":
    _log("[*] Tiêm môi trường thành công, chuẩn bị nổ máy...")
    asyncio.run(main())