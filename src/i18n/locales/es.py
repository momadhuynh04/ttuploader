LOCALE = {
    "browser_locale": "es-ES",
    "upload_button_selectors": [
        "[data-e2e='select_video_button']",
        "button:has-text('Seleccionar video')",
        "button:has-text('Subir')",
    ],
    "post_button_selectors": [
        "button[data-e2e='post_video_button']",
        "button:has-text('Publicar')",
    ],
    "caption_editor_selectors": [
        "div[contenteditable='true']",
        ".public-DraftEditor-content",
    ],
    "popup_dismiss_selectors": [
        "button:has-text('Permitir todas')",
        "button:has-text('Aceptar todas las cookies')",
        "button:has-text('Entendido')",
        "button:has-text('Activar')",
        "button:has-text('Confirmar')",
        ".tiktok-modal__close",
        "[aria-label='Close']",
    ],
    "force_post_selectors": [
        "button:has-text('Publicar de todos modos')",
        "button:has-text('Continuar')",
    ],
    "success_selectors": [
        "button:has-text('Gestionar posts')",
        "button:has-text('Subir otro video')",
        "div:has-text('Publicado')",
    ],
    "success_url_patterns": [
        "tiktokstudio/content",
        "/profile",
    ],
}
