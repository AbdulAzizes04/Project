"""
Structured logging module for EARTH VISION-X platform.
"""

import sys
import logging
from pathlib import Path

LOGS_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("EarthVisionX")
logger.setLevel(logging.INFO)

if not logger.handlers:
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(LOGS_DIR / "earth_vision_x.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
