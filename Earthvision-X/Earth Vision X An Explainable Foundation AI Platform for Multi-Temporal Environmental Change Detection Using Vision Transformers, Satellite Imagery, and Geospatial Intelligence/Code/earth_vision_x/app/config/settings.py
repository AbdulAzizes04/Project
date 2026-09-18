"""
Global Application Settings and Configuration Management for EARTH VISION-X.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

@dataclass
class AppConfig:
    PROJECT_NAME: str = "EARTH VISION-X"
    VERSION: str = "1.0.0"
    TAGLINE: str = "Explainable Foundation AI Platform for Multi-Temporal Satellite Change Detection"
    
    # Base Directories
    BASE_DIR: Path = BASE_DIR
    APP_DIR: Path = BASE_DIR / "earth_vision_x" / "app"
    MODELS_DIR: Path = BASE_DIR / "models"
    CHECKPOINTS_DIR: Path = BASE_DIR / "checkpoints"
    DATASETS_DIR: Path = BASE_DIR / "datasets"
    OUTPUTS_DIR: Path = BASE_DIR / "outputs"
    LOGS_DIR: Path = BASE_DIR / "logs"
    DOCS_DIR: Path = BASE_DIR / "docs"
    
    # Database Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'earth_vision_x.db'}")
    
    # Default Training Hyperparameters
    DEFAULT_BATCH_SIZE: int = 4
    DEFAULT_EPOCHS: int = 15
    DEFAULT_LR: float = 1e-4
    DEFAULT_IMAGE_SIZE: int = 256
    DEFAULT_DEVICE: str = "cuda" # Automatically falls back to cpu if unavailable
    
    # XAI Settings
    DEFAULT_XAI_METHOD: str = "Attention Rollout"

    def ensure_directories(self) -> None:
        """Create necessary directories if they do not exist."""
        for path in [
            self.MODELS_DIR,
            self.CHECKPOINTS_DIR,
            self.DATASETS_DIR,
            self.OUTPUTS_DIR,
            self.LOGS_DIR,
            self.DOCS_DIR,
        ]:
            path.mkdir(parents=True, exist_ok=True)

settings = AppConfig()
settings.ensure_directories()
