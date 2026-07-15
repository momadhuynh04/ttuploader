LOCALE = {
    "browser_locale": "fr-FR",
    "upload_button_selectors": [
        "[data-e2e='select_video_button']",
        "button:has-text('Sélectionner une vidéo')",
        "button:has-text('Télécharger')",
    ],
    "post_button_selectors": [
        "button[data-e2e='post_video_button']",
        "button:has-text('Publier')",
    ],
    "caption_editor_selectors": [
        "div[contenteditable='true']",
        ".public-DraftEditor-content",
    ],
    "popup_dismiss_selectors": [
        "button:has-text('Tout autoriser')",
        "button:has-text('Accepter tous les cookies')",
        "button:has-text(\"J'ai compris\")",
        "button:has-text('Activer')",
        "button:has-text('Confirmer')",
        ".tiktok-modal__close",
        "[aria-label='Close']",
    ],
    "force_post_selectors": [
        "button:has-text('Publier quand même')",
        "button:has-text('Continuer')",
    ],
    "success_selectors": [
        "button:has-text('Gérer les posts')",
        "button:has-text('Télécharger une autre vidéo')",
        "div:has-text('Publié')",
    ],
    "success_url_patterns": [
        "tiktokstudio/content",
        "/profile",
    ],
}
