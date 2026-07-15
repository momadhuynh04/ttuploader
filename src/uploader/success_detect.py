import asyncio


async def wait_for_upload_success(page, locale: dict, timeout: int = 60) -> bool:
    url_patterns = locale.get("success_url_patterns", [])
    selectors = locale.get("success_selectors", [])

    for _ in range(timeout * 2):
        current_url = page.url.lower()
        for pattern in url_patterns:
            if pattern in current_url:
                return True

        for sel in selectors:
            try:
                el = page.locator(sel).first
                if await el.count() > 0 and await el.is_visible(timeout=500):
                    return True
            except Exception:
                pass

        await asyncio.sleep(0.5)

    return False
