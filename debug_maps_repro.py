#!/usr/bin/env python
"""Quick repro: open one Google Maps search and save a screenshot.

Usage:
    python debug_maps_repro.py "estate in lekki"
    python debug_maps_repro.py "estate in lekki" --headful
    xvfb-run -a python debug_maps_repro.py "estate in lekki" --headful
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path

import click
from playwright.async_api import TimeoutError as PlaywrightTimeout

from config.settings import settings
from scraper.core.browser import BrowserManager
from scraper.utils.logger import log


@click.command()
@click.argument("query")
@click.option("--headful/--headless", default=True, help="Open the browser visibly for debugging.")
def main(query: str, headful: bool):
    """Open a single Google Maps search and save a screenshot."""
    has_display = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))

    if headful and not has_display:
        log.warning(
            "No X server detected. Falling back to headless mode. "
            "Use 'xvfb-run -a python debug_maps_repro.py <query> --headful' to run visibly."
        )
        settings.SCRAPER_HEADLESS = True
    else:
        settings.SCRAPER_HEADLESS = not headful

    settings.SCRAPER_VERBOSE_DUMPS = True
    settings.LOG_LEVEL = "DEBUG"
    asyncio.run(run(query))


async def run(query: str):
    browser = BrowserManager()
    await browser.start()
    page, context = await browser.new_page()
    try:
        search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
        log.info(f"Opening: {search_url}")
        await page.goto(search_url, wait_until="domcontentloaded", timeout=settings.SCRAPER_TIMEOUT)
        await asyncio.sleep(5)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in query)[:60]
        output_dir = Path(settings.SCREENSHOT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)

        screenshot_path = output_dir / f"quick_repro_{safe_name}_{ts}.png"
        html_path = Path(settings.LOG_DIR) / f"quick_repro_{safe_name}_{ts}.html"
        await page.screenshot(path=str(screenshot_path), full_page=False)
        html_path.write_text(await page.content(), encoding="utf-8")

        log.info(f"Saved screenshot: {screenshot_path}")
        log.info(f"Saved HTML: {html_path}")

    except PlaywrightTimeout as exc:
        log.error(f"Timeout while opening Maps search: {exc}")
    finally:
        await context.close()
        await browser.stop()


if __name__ == "__main__":
    main()
