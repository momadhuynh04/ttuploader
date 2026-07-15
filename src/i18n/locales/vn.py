LOCALE = {
    "browser_locale": "vi-VN",
    "upload_button_selectors": [
        "[data-e2e='select_video_button']",
        "button:has-text('Chọn video')",
        "button:has-text('Tải tập tin lên')",
        "div:has-text('Chọn video')",
        "label:has-text('Chọn video')",
    ],
    "post_button_selectors": [
        "button[data-e2e='post_video_button']",
        "button:has-text('Đăng')",
    ],
    "caption_editor_selectors": [
        "div[contenteditable='true']",
        ".public-DraftEditor-content",
    ],
    "popup_dismiss_selectors": [
        "button:has-text('Cho phép tất cả')",
        "button:has-text('Đã hiểu')",
        "button:has-text('Bật')",
        "button:has-text('Xác nhận')",
        ".tiktok-modal__close",
        "[aria-label='Close']",
    ],
    "force_post_selectors": [
        "button:has-text('Đăng ngay')",
        "button:has-text('Tiếp tục')",
    ],
    "success_selectors": [
        "button:has-text('Quản lý bài đăng')",
        "button:has-text('Tải video khác lên')",
        "div:has-text('Đã đăng lên')",
    ],
    "success_url_patterns": [
        "tiktokstudio/content",
        "/profile",
    ],
}
