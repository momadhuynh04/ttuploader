LOCALE = {
    "browser_locale": "pt-BR",
    "upload_button_selectors": [
        "[data-e2e='select_video_button']",
        "button:has-text('Selecionar vídeo')",
        "button:has-text('Enviar')",
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
        "button:has-text('Permitir todos')",
        "button:has-text('Aceitar todos os cookies')",
        "button:has-text('Entendi')",
        "button:has-text('Ativar')",
        "button:has-text('Confirmar')",
        ".tiktok-modal__close",
        "[aria-label='Close']",
    ],
    "force_post_selectors": [
        "button:has-text('Publicar mesmo assim')",
        "button:has-text('Continuar')",
    ],
    "success_selectors": [
        "button:has-text('Gerenciar posts')",
        "button:has-text('Enviar outro vídeo')",
        "div:has-text('Publicado')",
    ],
    "success_url_patterns": [
        "tiktokstudio/content",
        "/profile",
    ],
}
