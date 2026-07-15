LOCALE = {
    "browser_locale": "en-US",
    "upload_button_selectors": [
        "[data-e2e='select_video_button']",
        "button:has-text('Select video')",
        "button:has-text('Upload video')",
    ],
    "post_button_selectors": [
        "button[data-e2e='post_video_button']",
        "button:has-text('Post')",
    ],
    "caption_editor_selectors": [
        "div[contenteditable='true']",
        ".public-DraftEditor-content",
    ],
    "popup_dismiss_selectors": [
        "button:has-text('Allow all')",
        "button:has-text('Accept all cookies')",
        "button:has-text('Got it')",
        "button:has-text('Turn on')",
        "button:has-text('Confirm')",
        ".tiktok-modal__close",
        "[aria-label='Close']",
    ],
    "force_post_selectors": [
        "button:has-text('Post anyway')",
        "button:has-text('Post now')",
        "button:has-text('Continue')",
    ],
    "success_selectors": [
        "button:has-text('Manage posts')",
        "button:has-text('Upload another video')",
        "div:has-text('Uploaded')",
    ],
    "success_url_patterns": [
        "tiktokstudio/content",
        "/profile",
    ],
}
