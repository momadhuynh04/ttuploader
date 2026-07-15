from src.i18n.locales import en, vn, jp, kr, br, it, fr, de, es

LOCALE_MAP = {
    "US": en.LOCALE,
    "VN": vn.LOCALE,
    "JP": jp.LOCALE,
    "KR": kr.LOCALE,
    "BR": br.LOCALE,
    "IT": it.LOCALE,
    "FR": fr.LOCALE,
    "DE": de.LOCALE,
    "ES": es.LOCALE,
}

LOCALE_NAMES = {
    "US": "English",
    "VN": "Tiếng Việt",
    "JP": "日本語",
    "KR": "한국어",
    "BR": "Português",
    "IT": "Italiano",
    "FR": "Français",
    "DE": "Deutsch",
    "ES": "Español",
}

_FALLBACK_SELECTOR_KEYS = (
    "upload_button_selectors",
    "post_button_selectors",
    "popup_dismiss_selectors",
    "force_post_selectors",
    "success_selectors",
    "success_url_patterns",
)


def get_locale(region: str) -> dict:
    base = LOCALE_MAP.get(region.upper(), en.LOCALE)
    merged = dict(base)
    if region.upper() != "US":
        for key in _FALLBACK_SELECTOR_KEYS:
            region_vals = base.get(key, [])
            en_vals = en.LOCALE.get(key, [])
            merged[key] = list(dict.fromkeys(region_vals + en_vals))
    return merged


def get_name(region: str) -> str:
    return LOCALE_NAMES.get(region.upper(), "English")
