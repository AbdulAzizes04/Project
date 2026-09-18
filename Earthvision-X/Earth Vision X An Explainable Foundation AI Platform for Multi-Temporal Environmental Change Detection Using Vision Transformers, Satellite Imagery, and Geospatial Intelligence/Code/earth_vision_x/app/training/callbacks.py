"""
Training Callbacks: Early Stopping, Checkpoint Saver, and Metric Logger.
"""

import torch
from pathlib import Path
from earth_vision_x.app.config.logging_config import logger

class EarlyStopping:
    def __init__(self, patience: int = 5, min_delta: float = 1e-4):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_score = None
        self.early_stop = False

    def __call__(self, val_score: float) -> bool:
        if self.best_score is None:
            self.best_score = val_score
        elif val_score < self.best_score + self.min_delta:
            self.counter += 1
            logger.info(f"EarlyStopping counter: {self.counter} out of {self.patience}")
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_score = val_score
            self.counter = 0
        return self.early_stop

class CheckpointSaver:
    def __init__(self, checkpoint_dir: Path):
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def save(self, model: torch.nn.Module, epoch: int, metrics: dict, filename: str = "best_model.pth"):
        save_path = self.checkpoint_dir / filename
        checkpoint_data = {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "metrics": metrics
        }
        torch.save(checkpoint_data, save_path)
        logger.info(f"Checkpoint saved to: {save_path}")
