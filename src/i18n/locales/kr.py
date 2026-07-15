LOCALE = {
    "browser_locale": "ko-KR",
    "upload_button_selectors": [
        "[data-e2e='select_video_button']",
        "button:has-text('동영상 선택')",
        "button:has-text('업로드')",
    ],
    "post_button_selectors": [
        "button[data-e2e='post_video_button']",
        "button:has-text('게시')",
    ],
    "caption_editor_selectors": [
        "div[contenteditable='true']",
        ".public-DraftEditor-content",
    ],
    "popup_dismiss_selectors": [
        "button:has-text('모두 허용')",
        "button:has-text('모든 쿠키 허용')",
        "button:has-text('확인')",
        "button:has-text('켜기')",
        ".tiktok-modal__close",
        "[aria-label='Close']",
    ],
    "force_post_selectors": [
        "button:has-text('게시하기')",
        "button:has-text('계속')",
    ],
    "success_selectors": [
        "button:has-text('게시물 관리')",
        "button:has-text('다른 동영상 업로드')",
        "div:has-text('업로드됨')",
    ],
    "success_url_patterns": [
        "tiktokstudio/content",
        "/profile",
    ],
}
