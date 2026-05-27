# ============================================================
# scraper/core/maps_scraper.py
# Core Google Maps async scraper with retry and rate limiting
# ============================================================

import asyncio
import random
import re
import json
from typing import Optional
from urllib.parse import quote_plus
from datetime import datetime
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from playwright.async_api import Page, TimeoutError as PlaywrightTimeout

from config.settings import settings
from scraper.core.models import EstateRecord
from scraper.core.browser import BrowserManager
from scraper.utils.logger import log


class RateLimiter:
    """Async rate limiter using asyncio-throttle pattern."""

    def __init__(self, min_delay: float, max_delay: float):
        self.min_delay = min_delay
        self.max_delay = max_delay

    async def wait(self):
        delay = random.uniform(self.min_delay, self.max_delay)
        await asyncio.sleep(delay)


rate_limiter = RateLimiter(settings.SCRAPER_DELAY_MIN, settings.SCRAPER_DELAY_MAX)


class MapsDetailScraper:
    """
    Scrapes a single Google Maps place detail page.
    Called once we have a Maps URL for a listing.
    """

    async def scrape_detail(self, page: Page, url: str) -> dict:
        """Extract all available fields from a Maps place page."""
        data = {}
        try:
            await page.goto(url, wait_until="networkidle", timeout=settings.SCRAPER_TIMEOUT)
            await asyncio.sleep(random.uniform(1.5, 3.0))

            # ---- Name ----
            try:
                name_el = await page.query_selector("h1")
                if name_el:
                    data["name"] = (await name_el.inner_text()).strip()
            except Exception:
                pass

            # ---- Address ----
            try:
                addr_btn = await page.query_selector('button[data-item-id="address"]')
                if addr_btn:
                    data["address"] = (await addr_btn.get_attribute("aria-label") or "").replace("Address: ", "").strip()
            except Exception:
                pass

            # ---- Phone ----
            try:
                phone_btn = await page.query_selector('button[data-item-id^="phone"]')
                if phone_btn:
                    data["phone"] = (await phone_btn.get_attribute("aria-label") or "").replace("Phone: ", "").strip()
            except Exception:
                pass

            # ---- Website ----
            try:
                web_btn = await page.query_selector('a[data-item-id="authority"]')
                if web_btn:
                    data["website"] = await web_btn.get_attribute("href")
            except Exception:
                pass

            # ---- Rating ----
            try:
                rating_el = await page.query_selector('span[aria-hidden="true"].fontDisplayLarge')
                if rating_el:
                    data["rating"] = (await rating_el.inner_text()).strip()
            except Exception:
                pass

            # ---- Review count ----
            try:
                review_el = await page.query_selector('span[aria-label*="review"]')
                if review_el:
                    aria = await review_el.get_attribute("aria-label") or ""
                    match = re.search(r"([\d,]+)\s+review", aria)
                    if match:
                        data["review_count"] = int(match.group(1).replace(",", ""))
            except Exception:
                pass

            # ---- Category ----
            try:
                cat_el = await page.query_selector('button.DkEaL')
                if cat_el:
                    data["category"] = (await cat_el.inner_text()).strip()
            except Exception:
                pass

            # ---- Opening Hours ----
            try:
                hours_btn = await page.query_selector('div[data-hide-tooltip-on-mouse-move] table')
                if hours_btn:
                    rows = await hours_btn.query_selector_all("tr")
                    hours_parts = []
                    for row in rows[:7]:
                        text = (await row.inner_text()).strip().replace("\t", ": ")
                        hours_parts.append(text)
                    data["opening_hours"] = " | ".join(hours_parts)
            except Exception:
                pass

            # ---- Coordinates from URL ----
            try:
                current_url = page.url
                coord_match = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", current_url)
                if coord_match:
                    data["latitude"] = float(coord_match.group(1))
                    data["longitude"] = float(coord_match.group(2))
                data["maps_url"] = current_url
            except Exception:
                pass

            # ---- Place ID from URL ----
            try:
                pid_match = re.search(r"place/[^/]+/([^/]+)$", page.url)
                if pid_match:
                    data["place_id"] = pid_match.group(1)
            except Exception:
                pass

        except PlaywrightTimeout:
            log.warning(f"Timeout scraping detail page: {url}")
        except Exception as e:
            log.error(f"Error scraping detail for {url}: {e}")

        return data


class MapsSearchScraper:
    """
    Runs a Google Maps search, collects listing URLs,
    then scrapes each listing's detail page.
    """

    def __init__(self, browser_manager: BrowserManager):
        self.browser = browser_manager
        self.detail_scraper = MapsDetailScraper()

    @retry(
        stop=stop_after_attempt(settings.SCRAPER_MAX_RETRIES),
        wait=wait_exponential(multiplier=2, min=4, max=30),
        retry=retry_if_exception_type((PlaywrightTimeout, Exception)),
        reraise=True,
    )
    async def search_query(
        self, query: str, state: str, area: str, keyword: str
    ) -> list[EstateRecord]:
        """
        Execute one Google Maps search and return all scraped records.
        """
        records = []
        page, context = await self.browser.new_page()

        try:
            search_url = f"https://www.google.com/maps/search/{quote_plus(query)}"
            log.info(f"Searching: {query}")

            await page.goto(search_url, wait_until="domcontentloaded", timeout=settings.SCRAPER_TIMEOUT)
            await asyncio.sleep(random.uniform(2, 4))

            if settings.SCRAPER_VERBOSE_DUMPS:
                await self._write_debug_dump(page, query, "search_loaded")

            # Scroll to load more results
            listing_urls = await self._collect_listing_urls(page, query)
            log.info(f"Found {len(listing_urls)} listings for: {query}")

            # Scrape each listing
            for idx, url in enumerate(listing_urls):
                await rate_limiter.wait()
                try:
                    detail = await self.detail_scraper.scrape_detail(page, url)
                    if detail.get("name"):
                        record = EstateRecord(
                            name=detail.get("name", "Unknown"),
                            place_id=detail.get("place_id"),
                            maps_url=detail.get("maps_url", url),
                            address=detail.get("address"),
                            state=state,
                            area=area,
                            latitude=detail.get("latitude"),
                            longitude=detail.get("longitude"),
                            phone=detail.get("phone"),
                            website=detail.get("website"),
                            category=detail.get("category"),
                            rating=detail.get("rating"),
                            review_count=detail.get("review_count"),
                            opening_hours=detail.get("opening_hours"),
                            search_query=query,
                            search_keyword=keyword,
                        )
                        record.data_quality = record.compute_data_quality()
                        records.append(record)
                        log.debug(f"  [{idx+1}/{len(listing_urls)}] Scraped: {record.name}")
                except Exception as e:
                    log.warning(f"Failed scraping listing {url}: {e}")
                    await self.browser.take_screenshot(page, f"detail_error_{idx}")

        except PlaywrightTimeout:
            log.error(f"Timeout on search: {query}")
            await self.browser.take_screenshot(page, f"search_timeout")
            raise
        except Exception as e:
            log.error(f"Error on search '{query}': {e}")
            await self.browser.take_screenshot(page, f"search_error")
            raise
        finally:
            await context.close()

        return records

    async def _write_debug_dump(self, page: Page, query: str, suffix: str):
        """Save HTML and a screenshot for a search query."""
        try:
            safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", query)[:60]
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_path = Path(settings.LOG_DIR) / f"debug_{suffix}_{safe_name}_{ts}.html"
            html = await page.content()
            html_path.write_text(html, encoding="utf-8")
            await self.browser.take_screenshot(page, f"{suffix}_{safe_name}_{ts}")
            log.info(f"Saved debug dump for query '{query}' to {html_path}")
        except Exception as e:
            log.error(f"Failed to write debug dump for query '{query}': {e}")

    async def _collect_listing_urls(self, page: Page, query: str) -> list[str]:
        """Scroll through search results and collect all listing URLs."""
        urls = []
        max_scrolls = max(1, settings.SCRAPER_MAX_RESULTS_PER_SEARCH // 7)

        try:
            # Wait for results panel
            await page.wait_for_selector('div[role="feed"]', timeout=10000)
            feed = await page.query_selector('div[role="feed"]')

            for scroll_n in range(max_scrolls):
                # Collect current listings
                items = await page.query_selector_all('a[href*="/maps/place/"]')
                for item in items:
                    href = await item.get_attribute("href")
                    if href and href not in urls and "/maps/place/" in href:
                        urls.append(href)

                if len(urls) >= settings.SCRAPER_MAX_RESULTS_PER_SEARCH:
                    break

                # Check for "end of list"
                end_marker = await page.query_selector('span.HlvSq')
                if end_marker:
                    break

                # Scroll the feed
                if feed:
                    await feed.evaluate("el => el.scrollBy(0, 1200)")
                    await asyncio.sleep(random.uniform(1.2, 2.5))

        except Exception as e:
            log.warning(f"Could not collect listing URLs fully: {e}")

        # Deduplicate while preserving order
        seen = set()
        unique_urls = []
        for u in urls:
            base = u.split("?")[0]
            if base not in seen:
                seen.add(base)
                unique_urls.append(u)

        # Diagnostic: if no URLs found, save page HTML + screenshot for debugging (useful on headless VMs)
        if not unique_urls:
            try:
                await self._write_debug_dump(page, query, "no_listings")
                log.warning(f"No listing URLs collected for query '{query}'.")
            except Exception as e:
                log.error(f"Failed to write debug dump for query '{query}': {e}")

        return unique_urls[:settings.SCRAPER_MAX_RESULTS_PER_SEARCH]
