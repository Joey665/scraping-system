# ============================================================
# scraper/utils/proxy_manager.py
# Rotating proxy support
# ============================================================

import random
from pathlib import Path
from typing import Optional
from scraper.utils.logger import log
from config.settings import settings


class ProxyManager:
    """Manages a pool of rotating proxies for scraping sessions."""

    def __init__(self):
        self.proxies: list[str] = []
        self.current_index: int = 0
        self.failed: set[str] = set()
        self._load_proxies()

    def _load_proxies(self):
        """Load proxies from file or single proxy env var."""
        if not settings.PROXY_ENABLED:
            log.info("Proxy rotation disabled.")
            return

        if settings.PROXY_SINGLE:
            self.proxies = [settings.PROXY_SINGLE]
            log.info(f"Single proxy loaded: {settings.PROXY_SINGLE[:30]}...")
            return

        if settings.PROXY_LIST_FILE:
            proxy_file = Path(settings.PROXY_LIST_FILE)
            if proxy_file.exists():
                raw = proxy_file.read_text(encoding="utf-8").strip().splitlines()
                self.proxies = [line.strip() for line in raw if line.strip() and not line.startswith("#")]
                log.info(f"Loaded {len(self.proxies)} proxies from {proxy_file}")
            else:
                log.warning(f"Proxy file not found: {proxy_file}")

    def get_proxy(self) -> Optional[dict]:
        """Return the next available proxy dict for Playwright."""
        if not self.proxies:
            return None

        available = [p for p in self.proxies if p not in self.failed]
        if not available:
            log.warning("All proxies have failed. Resetting failed set.")
            self.failed.clear()
            available = self.proxies

        proxy_str = random.choice(available)
        return self._parse_proxy(proxy_str)

    def mark_failed(self, proxy: str):
        """Mark a proxy as failed so it won't be reused immediately."""
        self.failed.add(proxy)
        log.warning(f"Proxy marked as failed: {proxy[:30]}...")

    @staticmethod
    def _parse_proxy(proxy_str: str) -> dict:
        """
        Parse proxy string into Playwright-compatible dict.
        Supports: protocol://user:pass@host:port or protocol://host:port
        """
        if "://" not in proxy_str:
            proxy_str = "http://" + proxy_str

        result = {"server": proxy_str}

        # Extract credentials if present
        parts = proxy_str.split("://", 1)
        if "@" in parts[1]:
            creds, host_port = parts[1].rsplit("@", 1)
            if ":" in creds:
                username, password = creds.split(":", 1)
                result["username"] = username
                result["password"] = password
            result["server"] = f"{parts[0]}://{host_port}"

        return result


proxy_manager = ProxyManager()
