LOCALE = {
    "browser_locale": "de-DE",
    "upload_button_selectors": [
        "[data-e2e='select_video_button']",
        "button:has-text('Video auswählen')",
        "button:has-text('Hochladen')",
    ],
    "post_button_selectors": [
        "button[data-e2e='post_video_button']",
        "button:has-text('Posten')",
    ],
    "caption_editor_selectors": [
        "div[contenteditable='true']",
        ".public-DraftEditor-content",
    ],
    "popup_dismiss_selectors": [
        "button:has-text('Alle erlauben')",
        "button:has-text('Alle akzeptieren')",
        "button:has-text('Verstanden')",
        "button:has-text('Aktivieren')",
        "button:has-text('Bestätigen')",
        ".tiktok-modal__close",
        "[aria-label='Close']",
    ],
    "force_post_selectors": [
        "button:has-text('Trotzdem posten')",
        "button:has-text('Fortfahren')",
    ],
    "success_selectors": [
        "button:has-text('Beiträge verwalten')",
        "button:has-text('Weiteres Video hochladen')",
        "div:has-text('Hochgeladen')",
    ],
    "success_url_patterns": [
        "tiktokstudio/content",
        "/profile",
    ],
}
