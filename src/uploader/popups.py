import asyncio


async def dismiss_popups(page, selectors: list[str]):
    for selector in selectors:
        try:
            btn = page.locator(selector).first
            if await btn.count() > 0:
                if await btn.is_visible(timeout=1000):
                    await btn.click()
                    await asyncio.sleep(0.3)
        except Exception:
            pass
