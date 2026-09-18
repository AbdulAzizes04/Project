"""
General utility functions for logging, reproducibility, and file management.
"""

import os
import random
import logging
from pathlib import Path
import numpy as np
import torch
from backend.config import RANDOM_SEED

def set_seed(seed: int = RANDOM_SEED) -> None:
    """Sets random seeds across Python, NumPy, and PyTorch for guaranteed reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    os.environ["PYTHONHASHSEED"] = str(seed)

def setup_logger(name: str = "QuantumMedCompress") -> logging.Logger:
    """Configures a standardized console and stream logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger

def get_file_size_bytes(filepath: Path | str) -> int:
    """Returns size of a file in bytes."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path.stat().st_size
