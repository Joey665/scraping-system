# ============================================================
# config/settings.py
# Central configuration — reads from .env
# ============================================================

from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    OUTPUT_DIR: Path = Field(default=Path("data/exports"))
    RAW_DATA_DIR: Path = Field(default=Path("data/raw"))
    CLEANED_DATA_DIR: Path = Field(default=Path("data/cleaned"))
    SCREENSHOT_DIR: Path = Field(default=Path("screenshots"))
    LOG_DIR: Path = Field(default=Path("logs"))

    # Scraper behaviour
    SCRAPER_HEADLESS: bool = True
    SCRAPER_VERBOSE_DUMPS: bool = False
    SCRAPER_SLOW_MO: int = 50
    SCRAPER_TIMEOUT: int = 30000
    SCRAPER_MAX_RETRIES: int = 3
    SCRAPER_DELAY_MIN: float = 2.5
    SCRAPER_DELAY_MAX: float = 6.0
    SCRAPER_BATCH_SIZE: int = 50
    SCRAPER_MAX_RESULTS_PER_SEARCH: int = 120
    SCRAPER_CONCURRENT_TABS: int = 2

    # Proxy
    PROXY_ENABLED: bool = False
    PROXY_LIST_FILE: Optional[str] = None
    PROXY_SINGLE: Optional[str] = None

    # Logging
    LOG_LEVEL: str = "INFO"

    # Lead scoring weights
    SCORE_WEIGHT_REVIEWS: float = 0.25
    SCORE_WEIGHT_RATING: float = 0.15
    SCORE_WEIGHT_HAS_WEBSITE: float = 0.20
    SCORE_WEIGHT_LUXURY_KEYWORDS: float = 0.25
    SCORE_WEIGHT_HAS_PHONE: float = 0.15

    # Azure
    AZURE_STORAGE_ACCOUNT: Optional[str] = None
    AZURE_STORAGE_KEY: Optional[str] = None
    AZURE_CONTAINER_NAME: str = "bracken-leads"

    # External APIs
    HUNTER_API_KEY: Optional[str] = None
    SLACK_WEBHOOK_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def ensure_dirs(self):
        """Create all required directories."""
        for d in [
            self.OUTPUT_DIR,
            self.RAW_DATA_DIR,
            self.CLEANED_DATA_DIR,
            self.SCREENSHOT_DIR,
            self.LOG_DIR,
        ]:
            Path(d).mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
