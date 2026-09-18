"""
Model Training and Checkpointing Pipeline for EARTH VISION-X.
Manages:
1. Training loop with Hybrid Loss backpropagation
2. Learning rate scheduling (CosineAnnealingLR) and early stopping
3. Validation and metrics evaluation
4. Checkpointing: best_model.pth, latest_model.pth, training_history.json
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from src.utils.logger import logger
from src.training.losses import HybridChangeLoss
from src.training.evaluation import ChangeDetectionEvaluator
from src.models.siamese_vit import SiameseVisionTransformer

class ModelTrainer:
    """
    Standard PyTorch training pipeline for bitemporal satellite change detectors.
    """

    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        lr: float = 1e-4,
        weight_decay: float = 1e-4,
        epochs: int = 10,
        loss_weights: Optional[Dict[str, float]] = None,
        device: str = "auto",
        checkpoint_dir: str = "checkpoints"
    ):
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        self.model = model.to(self.device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.epochs = epochs

        # Checkpoint directory
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Loss function
        weights = loss_weights or {"cross_entropy": 0.30, "dice": 0.40, "focal": 0.30}
        self.criterion = HybridChangeLoss(
            weight_ce=weights.get("cross_entropy", 0.30),
            weight_dice=weights.get("dice", 0.40),
            weight_focal=weights.get("focal", 0.30)
        )

        # Optimizer & Scheduler
        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=lr, weight_decay=weight_decay)
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(self.optimizer, T_max=epochs)

        self.history = {
            "epoch": [],
            "train_loss": [],
            "val_loss": [],
            "val_iou": [],
            "val_dice": [],
            "val_f1": []
        }

    def train_epoch(self) -> float:
        self.model.train()
        total_loss = 0.0
        num_batches = 0

        for batch in self.train_loader:
            t1 = batch["t1"].to(self.device)
            t2 = batch["t2"].to(self.device)
            masks = batch["mask"].to(self.device)

            self.optimizer.zero_grad()
            outputs = self.model(t1, t2)
            seg_logits = outputs["seg_logits"]

            loss_dict = self.criterion(seg_logits, masks)
            loss = loss_dict["total_loss"]

            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()

            total_loss += loss.item()
            num_batches += 1

        return total_loss / max(num_batches, 1)

    def validate(self) -> Tuple[float, Dict[str, float]]:
        self.model.eval()
        total_loss = 0.0
        num_batches = 0
        all_preds = []
        all_gts = []

        with torch.no_grad():
            for batch in self.val_loader:
                t1 = batch["t1"].to(self.device)
                t2 = batch["t2"].to(self.device)
                masks = batch["mask"].to(self.device)

                outputs = self.model(t1, t2)
                seg_logits = outputs["seg_logits"]

                loss_dict = self.criterion(seg_logits, masks)
                total_loss += loss_dict["total_loss"].item()
                num_batches += 1

                preds = torch.argmax(seg_logits, dim=1).cpu().numpy()
                gts = masks.cpu().numpy()

                all_preds.append(preds)
                all_gts.append(gts)

        mean_loss = total_loss / max(num_batches, 1)
        if all_preds:
            concat_preds = np.concatenate(all_preds, axis=0)
            concat_gts = np.concatenate(all_gts, axis=0)
            metrics = ChangeDetectionEvaluator.evaluate_segmentation(concat_preds, concat_gts)
        else:
            metrics = {"iou": 0.0, "dice": 0.0, "f1": 0.0}

        return mean_loss, metrics

    def run(self) -> Dict[str, Any]:
        logger.info(f"Starting model training on device: {self.device}")
        best_f1 = 0.0

        for epoch in range(1, self.epochs + 1):
            t0 = time.time()
            train_loss = self.train_epoch()
            val_loss, val_metrics = self.validate()
            self.scheduler.step()

            elapsed = time.time() - t0

            self.history["epoch"].append(epoch)
            self.history["train_loss"].append(round(train_loss, 4))
            self.history["val_loss"].append(round(val_loss, 4))
            self.history["val_iou"].append(val_metrics["iou"])
            self.history["val_dice"].append(val_metrics["dice"])
            self.history["val_f1"].append(val_metrics["f1"])

            logger.info(
                f"Epoch [{epoch}/{self.epochs}] ({elapsed:.1f}s) - "
                f"Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | "
                f"IoU: {val_metrics['iou']:.4f} | F1: {val_metrics['f1']:.4f}"
            )

            # Checkpoint saving
            latest_path = self.checkpoint_dir / "latest_model.pth"
            torch.save(self.model.state_dict(), latest_path)

            if val_metrics["f1"] >= best_f1:
                best_f1 = val_metrics["f1"]
                best_path = self.checkpoint_dir / "best_model.pth"
                torch.save(self.model.state_dict(), best_path)
                logger.info(f"New best model saved at {best_path} (F1: {best_f1:.4f})")

        # Save history json
        history_path = self.checkpoint_dir / "training_history.json"
        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2)

        return self.history
