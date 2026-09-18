"""
Structured Logging Configuration for EARTH VISION-X.
"""

import logging
import sys
from pathlib import Path
from earth_vision_x.app.config.settings import settings

def setup_logger(name: str = "EarthVisionX") -> logging.Logger:
    """Configures and returns a logger instance with console and file handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if logger.handlers:
        return logger
        
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler
    log_file = settings.LOGS_DIR / "earth_vision_x.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logger()
