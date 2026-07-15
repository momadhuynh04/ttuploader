LOCALE = {
    "browser_locale": "it-IT",
    "upload_button_selectors": [
        "[data-e2e='select_video_button']",
        "button:has-text('Seleziona video')",
        "button:has-text('Carica')",
    ],
    "post_button_selectors": [
        "button[data-e2e='post_video_button']",
        "button:has-text('Pubblica')",
    ],
    "caption_editor_selectors": [
        "div[contenteditable='true']",
        ".public-DraftEditor-content",
    ],
    "popup_dismiss_selectors": [
        "button:has-text('Accetta tutti')",
        "button:has-text('Accetta tutti i cookie')",
        "button:has-text('Ho capito')",
        "button:has-text('Attiva')",
        "button:has-text('Conferma')",
        ".tiktok-modal__close",
        "[aria-label='Close']",
    ],
    "force_post_selectors": [
        "button:has-text('Pubblica comunque')",
        "button:has-text('Continua')",
    ],
    "success_selectors": [
        "button:has-text('Gestisci post')",
        "button:has-text('Carica un altro video')",
        "div:has-text('Pubblicato')",
    ],
    "success_url_patterns": [
        "tiktokstudio/content",
        "/profile",
    ],
}
