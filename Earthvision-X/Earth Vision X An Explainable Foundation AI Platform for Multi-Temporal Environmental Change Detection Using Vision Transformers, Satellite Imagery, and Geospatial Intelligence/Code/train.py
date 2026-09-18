"""
CLI Training Tool for EARTH VISION-X.
Usage: python train.py --model "ViT-Base Siamese" --epochs 10 --batch-size 4 --lr 0.0001
"""

import sys
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from earth_vision_x.app.config.constants import SupportedModels, SupportedLosses, SupportedOptimizers
from earth_vision_x.app.config.logging_config import logger
from earth_vision_x.app.database.db import init_db
from earth_vision_x.app.services.training_service import TrainingService

def main():
    parser = argparse.ArgumentParser(description="EARTH VISION-X Model Training CLI")
    parser.add_argument("--model", type=str, default=SupportedModels.VIT_BASE.value, help="Model architecture")
    parser.add_argument("--loss", type=str, default=SupportedLosses.HYBRID_LOSS.value, help="Loss function")
    parser.add_argument("--optimizer", type=str, default=SupportedOptimizers.ADAMW.value, help="Optimizer")
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=2, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--device", type=str, default="cpu", help="Device (cpu or cuda)")

    args = parser.parse_args()

    logger.info("Initializing EARTH VISION-X CLI Training Engine...")
    init_db()

    history = TrainingService.train_model(
        model_name=args.model,
        loss_name=args.loss,
        optimizer_name=args.optimizer,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        device=args.device
    )

    logger.info(f"Training run completed! Final Val Loss: {history['val_loss'][-1]:.4f} | Best F1: {max(history['f1_score']):.4f}")

if __name__ == "__main__":
    main()
