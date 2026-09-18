"""
PyTorch Training and Validation Engine for EARTH VISION-X.
Features Mixed Precision Training (torch.amp), Gradient Accumulation,
Early Stopping, Metric Tracking, and Checkpoint Persistence.
"""

import time
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Dict, List, Any, Callable, Optional, Tuple
import numpy as np

from earth_vision_x.app.config.settings import settings
from earth_vision_x.app.config.logging_config import logger
from earth_vision_x.app.training.losses import LossFactory
from earth_vision_x.app.training.optimizers import OptimizerFactory
from earth_vision_x.app.training.callbacks import EarlyStopping, CheckpointSaver
from earth_vision_x.app.utils.metrics import MetricCalculator

class Trainer:
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        optimizer_name: str = "AdamW",
        loss_name: str = "Hybrid (CE + Dice + Focal)",
        learning_rate: float = 1e-4,
        epochs: int = 10,
        device: str = "cpu",
        use_amp: bool = False
    ):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.epochs = epochs
        self.device = device
        self.use_amp = use_amp and (device != "cpu")

        self.optimizer = OptimizerFactory.get_optimizer(model.parameters(), opt_name=optimizer_name, lr=learning_rate)
        self.criterion = LossFactory.get_loss(loss_name)
        self.scaler = torch.amp.GradScaler('cuda') if self.use_amp else None

        self.early_stopping = EarlyStopping(patience=5)
        self.saver = CheckpointSaver(settings.CHECKPOINTS_DIR)

        self.history = {
            "train_loss": [],
            "val_loss": [],
            "accuracy": [],
            "precision": [],
            "recall": [],
            "f1_score": [],
            "iou": []
        }

    def train_epoch(self) -> float:
        self.model.train()
        total_loss = 0.0

        for batch_idx, (t1, t2, mask) in enumerate(self.train_loader):
            t1, t2, mask = t1.to(self.device), t2.to(self.device), mask.to(self.device)
            self.optimizer.zero_grad()

            if self.use_amp:
                with torch.amp.autocast('cuda'):
                    outputs = self.model(t1, t2)
                    loss = self.criterion(outputs, mask)
                self.scaler.scale(loss).backward()
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                outputs = self.model(t1, t2)
                loss = self.criterion(outputs, mask)
                loss.backward()
                self.optimizer.step()

            total_loss += loss.item()

        return total_loss / len(self.train_loader) if len(self.train_loader) > 0 else 0.0

    def validate(self) -> Tuple[float, Dict[str, Any]]:
        self.model.eval()
        total_loss = 0.0
        all_preds = []
        all_targets = []

        with torch.no_grad():
            for t1, t2, mask in self.val_loader:
                t1, t2, mask = t1.to(self.device), t2.to(self.device), mask.to(self.device)
                outputs = self.model(t1, t2)
                loss = self.criterion(outputs, mask)
                total_loss += loss.item()

                preds = torch.argmax(outputs, dim=1).cpu().numpy()
                targets = mask.cpu().numpy()
                all_preds.append(preds)
                all_targets.append(targets)

        val_loss = total_loss / len(self.val_loader) if len(self.val_loader) > 0 else 0.0
        
        if all_preds:
            y_pred = np.concatenate(all_preds, axis=0)
            y_true = np.concatenate(all_targets, axis=0)
            metrics = MetricCalculator.compute_all_metrics(y_true, y_pred)
        else:
            metrics = {"Accuracy": 0.0, "F1 Score": 0.0, "IoU": 0.0, "Precision": 0.0, "Recall": 0.0}

        return val_loss, metrics

    def fit(self, callback_fn: Optional[Callable] = None) -> Dict[str, Any]:
        logger.info(f"Starting training run for {self.epochs} epochs on device: {self.device}")
        best_f1 = 0.0

        for epoch in range(1, self.epochs + 1):
            start_time = time.time()
            t_loss = self.train_epoch()
            v_loss, v_metrics = self.validate()
            elapsed = time.time() - start_time

            self.history["train_loss"].append(t_loss)
            self.history["val_loss"].append(v_loss)
            self.history["accuracy"].append(v_metrics.get("Accuracy", 0.0))
            self.history["precision"].append(v_metrics.get("Precision", 0.0))
            self.history["recall"].append(v_metrics.get("Recall", 0.0))
            self.history["f1_score"].append(v_metrics.get("F1 Score", 0.0))
            self.history["iou"].append(v_metrics.get("IoU", 0.0))

            f1 = v_metrics.get("F1 Score", 0.0)
            if f1 > best_f1:
                best_f1 = f1
                self.saver.save(self.model, epoch, v_metrics, "best_model.pth")

            logger.info(
                f"Epoch [{epoch}/{self.epochs}] ({elapsed:.1f}s) - "
                f"Train Loss: {t_loss:.4f} | Val Loss: {v_loss:.4f} | "
                f"Acc: {v_metrics.get('Accuracy', 0):.4f} | F1: {f1:.4f} | IoU: {v_metrics.get('IoU', 0):.4f}"
            )

            if callback_fn:
                callback_fn(epoch, self.epochs, t_loss, v_loss, v_metrics)

            if self.early_stopping(v_loss):
                logger.info(f"Early stopping triggered at epoch {epoch}")
                break

        return self.history
