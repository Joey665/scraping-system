# ============================================================
# scraper/core/browser.py
# Playwright browser lifecycle management
# ============================================================

import asyncio
import random
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright

from config.settings import settings
from scraper.utils.user_agents import get_random_user_agent
from scraper.utils.proxy_manager import proxy_manager
from scraper.utils.logger import log


class BrowserManager:
    """Manages Playwright browser lifecycle with anti-detection measures."""

    def __init__(self):
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None

    async def start(self):
        """Launch browser instance."""
        self._playwright = await async_playwright().start()

        launch_args = {
            "headless": settings.SCRAPER_HEADLESS,
            "slow_mo": settings.SCRAPER_SLOW_MO,
            "args": [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--disable-gpu",
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
            ],
        }

        proxy = proxy_manager.get_proxy()
        if proxy:
            launch_args["proxy"] = proxy
            log.info(f"Browser started with proxy: {proxy['server']}")
        else:
            log.info("Browser started without proxy.")

        self._browser = await self._playwright.chromium.launch(**launch_args)
        return self

    async def new_context(self) -> BrowserContext:
        """Create a new browser context with fresh fingerprint."""
        user_agent = get_random_user_agent()
        viewport = random.choice([
            {"width": 1920, "height": 1080},
            {"width": 1440, "height": 900},
            {"width": 1366, "height": 768},
            {"width": 1536, "height": 864},
        ])

        context = await self._browser.new_context(
            user_agent=user_agent,
            viewport=viewport,
            locale="en-NG",
            timezone_id="Africa/Lagos",
            geolocation={"latitude": 6.5244, "longitude": 3.3792},  # Lagos coords
            permissions=["geolocation"],
            extra_http_headers={
                "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            },
        )

        # Inject anti-detection JS
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-GB', 'en'] });
            window.chrome = { runtime: {} };
        """)

        return context

    async def new_page(self) -> tuple[Page, BrowserContext]:
        """Open a new page within a fresh context."""
        context = await self.new_context()
        page = await context.new_page()
        page.set_default_timeout(settings.SCRAPER_TIMEOUT)
        return page, context

    async def take_screenshot(self, page: Page, label: str):
        """Capture a screenshot on failure."""
        path = Path(settings.SCREENSHOT_DIR) / f"{label}_{asyncio.get_event_loop().time():.0f}.png"
        try:
            await page.screenshot(path=str(path), full_page=False)
            log.warning(f"Screenshot saved: {path}")
        except Exception as e:
            log.error(f"Could not save screenshot: {e}")

    async def stop(self):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        log.info("Browser closed.")

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, *args):
        await self.stop()
