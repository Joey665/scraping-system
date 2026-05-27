# ============================================================
# scraper/utils/user_agents.py
# Rotating user agents to avoid fingerprinting
# ============================================================

import random
from fake_useragent import UserAgent

# Curated realistic desktop Chrome user-agents as fallback
FALLBACK_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
]

_ua = None


def _init_ua():
    global _ua
    try:
        _ua = UserAgent(browsers=["chrome", "firefox", "edge"], os=["windows", "macos", "linux"])
    except Exception:
        _ua = None


def get_random_user_agent() -> str:
    """Return a random realistic desktop user-agent string."""
    global _ua
    if _ua is None:
        _init_ua()
    try:
        if _ua:
            return _ua.random
    except Exception:
        pass
    return random.choice(FALLBACK_USER_AGENTS)


def get_chrome_user_agent() -> str:
    """Return specifically a Chrome user-agent."""
    chrome_agents = [ua for ua in FALLBACK_USER_AGENTS if "Chrome" in ua and "Edg" not in ua]
    return random.choice(chrome_agents)
