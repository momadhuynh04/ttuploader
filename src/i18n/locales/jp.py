LOCALE = {
    "browser_locale": "ja-JP",
    "upload_button_selectors": [
        "[data-e2e='select_video_button']",
        "button:has-text('動画を選択')",
        "button:has-text('アップロード')",
    ],
    "post_button_selectors": [
        "button[data-e2e='post_video_button']",
        "button:has-text('投稿')",
    ],
    "caption_editor_selectors": [
        "div[contenteditable='true']",
        ".public-DraftEditor-content",
    ],
    "popup_dismiss_selectors": [
        "button:has-text('すべて許可')",
        "button:has-text('すべてのCookieを受け入れる')",
        "button:has-text('了解')",
        "button:has-text('オンにする')",
        "button:has-text('確認')",
        ".tiktok-modal__close",
        "[aria-label='Close']",
    ],
    "force_post_selectors": [
        "button:has-text('投稿する')",
        "button:has-text('続行')",
    ],
    "success_selectors": [
        "button:has-text('投稿を管理')",
        "button:has-text('別の動画をアップロード')",
        "div:has-text('投稿されました')",
    ],
    "success_url_patterns": [
        "tiktokstudio/content",
        "/profile",
    ],
}
