# ============================================================
# scraper/utils/logger.py
# Structured logging with loguru + rich output
# ============================================================

import sys
from pathlib import Path
from loguru import logger
from datetime import datetime

from config.settings import settings


def setup_logger(name: str = "bracken_scraper") -> "logger":
    """Configure and return the application logger."""
    log_file = Path(settings.LOG_DIR) / f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logger.remove()

    # Console output — colored, human-readable
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{line}</cyan> — "
            "<level>{message}</level>"
        ),
        colorize=True,
    )

    # File output — full detail, JSON-structured
    logger.add(
        str(log_file),
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{line} | {message}",
        rotation="50 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
    )

    logger.info(f"Logger initialised. Log file: {log_file}")
    return logger


log = setup_logger()
