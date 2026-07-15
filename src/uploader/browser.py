import base64
import json
from urllib.parse import urlparse

from phantomwright.async_api import async_playwright, Browser, BrowserContext, Page
from phantomwright.stealth import Stealth

from src.i18n.base import get_locale


VALID_SAME_SITE = {"Strict", "Lax", "None"}

_NAV_LANGUAGES = {
    "US": ("en-US", "en"),
    "VN": ("vi-VN", "vi"),
    "JP": ("ja-JP", "ja"),
    "KR": ("ko-KR", "ko"),
    "BR": ("pt-BR", "pt"),
    "IT": ("it-IT", "it"),
    "FR": ("fr-FR", "fr"),
    "DE": ("de-DE", "de"),
    "ES": ("es-ES", "es"),
}


def _locale_to_languages_override(region: str) -> tuple[str, str]:
    return _NAV_LANGUAGES.get(region.upper(), ("en-US", "en"))


def decode_cookie(raw: str) -> list[dict]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        try:
            data = json.loads(base64.b64decode(raw).decode("utf-8"))
        except Exception:
            return []
    if not isinstance(data, list):
        return []
    normalized = []
    for cookie in data:
        if not isinstance(cookie, dict):
            continue
        if "name" not in cookie or "value" not in cookie:
            continue
        cleaned = {
            "name": cookie["name"],
            "value": cookie["value"],
            "domain": cookie.get("domain", ""),
            "path": cookie.get("path", "/"),
        }
        if "expirationDate" in cookie:
            cleaned["expires"] = cookie["expirationDate"]
        elif "expires" in cookie:
            cleaned["expires"] = cookie["expires"]
        if "httpOnly" in cookie:
            cleaned["httpOnly"] = bool(cookie["httpOnly"])
        if "secure" in cookie:
            cleaned["secure"] = bool(cookie["secure"])
        same_site = cookie.get("sameSite")
        if same_site in VALID_SAME_SITE:
            cleaned["sameSite"] = same_site
        elif same_site == "no_restriction":
            cleaned["sameSite"] = "None"
        normalized.append(cleaned)
    return normalized


def parse_proxy(proxy_url: str) -> dict | None:
    if not proxy_url:
        return None
    parsed = urlparse(proxy_url)
    p = {"server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"}
    if parsed.username and parsed.password:
        p["username"] = parsed.username
        p["password"] = parsed.password
    return p


class BrowserSession:
    def __init__(self, proxy_url: str, region: str, cookie_raw: str, headless: bool = False):
        self.proxy_url = proxy_url
        self.region = region.upper()
        self.cookie_raw = cookie_raw
        self.headless = headless
        self._playwright = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    @property
    def page(self) -> Page:
        if self._page is None:
            raise RuntimeError("Browser not launched. Call launch() first.")
        return self._page

    @property
    def browser(self) -> Browser:
        if self._browser is None:
            raise RuntimeError("Browser not launched. Call launch() first.")
        return self._browser

    async def launch(self):
        locale = get_locale(self.region)
        locale_str = locale["browser_locale"]
        proxy = parse_proxy(self.proxy_url)
        cookies = decode_cookie(self.cookie_raw)

        self._playwright = await async_playwright().start()

        launch_kwargs: dict = {
            "headless": self.headless,
            "args": [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
            ],
        }
        if proxy:
            launch_kwargs["proxy"] = proxy

        self._browser = await self._playwright.chromium.launch(**launch_kwargs)

        self._context = await self._browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale=locale_str,
        )

        lang_override = _locale_to_languages_override(self.region)
        stealth = Stealth(
            chrome_runtime=True,
            navigator_languages_override=lang_override,
            navigator_platform_override="Win32",
            navigator_hardware_concurrency=8,
        )
        await stealth.apply_stealth_async(self._context)

        if cookies:
            await self._context.add_cookies(cookies)

        self._page = await self._context.new_page()

        async def _resource_blocker(route):
            if route.request.resource_type in ("image", "media"):
                await route.abort()
            else:
                await route.continue_()
        await self._page.route("**/*", _resource_blocker)

    async def close(self):
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def goto(self, url: str):
        if url not in self.page.url:
            await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)

    async def disable_file_picker(self):
        await self.page.evaluate("""() => {
            try {
                if ('showOpenFilePicker' in window) {
                    delete window.showOpenFilePicker;
                }
            } catch(e) {}
            try {
                Object.defineProperty(window, 'showOpenFilePicker', {
                    get: () => undefined, configurable: true
                });
            } catch(e) {}
        }""")
