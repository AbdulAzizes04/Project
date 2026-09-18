"""
Training Business Service Layer.
Manages dataset preparation, training execution, metric recording, and model checkpoint registration.
"""

from typing import Dict, Any, Callable, Optional
from torch.utils.data import DataLoader

from earth_vision_x.app.config.constants import SupportedModels, SupportedLosses, SupportedOptimizers
from earth_vision_x.app.config.logging_config import logger
from earth_vision_x.app.models.factory import ModelFactory
from earth_vision_x.app.datasets.sample_downloader import SampleDatasetGenerator
from earth_vision_x.app.datasets.sentinel2_dataset import Sentinel2ChangeDataset
from earth_vision_x.app.training.trainer import Trainer
from earth_vision_x.app.database.db import SessionLocal
from earth_vision_x.app.database.repository import TrainingRunRepository
from earth_vision_x.app.database.models import TrainingRun

class TrainingService:
    @staticmethod
    def train_model(
        model_name: str = SupportedModels.VIT_BASE,
        loss_name: str = SupportedLosses.HYBRID_LOSS,
        optimizer_name: str = SupportedOptimizers.ADAMW,
        epochs: int = 5,
        batch_size: int = 2,
        lr: float = 1e-4,
        device: str = "cpu",
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Executes model training run and logs results to database.
        """
        # Ensure sample dataset exists
        samples = SampleDatasetGenerator.generate_synthetic_benchmark(num_samples=8)
        
        train_ds = Sentinel2ChangeDataset(
            t1_paths=samples["t1_paths"][:6],
            t2_paths=samples["t2_paths"][:6],
            mask_paths=samples["mask_paths"][:6],
            is_training=True
        )
        val_ds = Sentinel2ChangeDataset(
            t1_paths=samples["t1_paths"][6:],
            t2_paths=samples["t2_paths"][6:],
            mask_paths=samples["mask_paths"][6:],
            is_training=False
        )

        train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)

        model = ModelFactory.create_model(model_type=model_name, device=device)

        trainer = Trainer(
            model=model,
            train_loader=train_loader,
            val_loader=val_loader,
            optimizer_name=optimizer_name,
            loss_name=loss_name,
            learning_rate=lr,
            epochs=epochs,
            device=device
        )

        history = trainer.fit(callback_fn=progress_callback)

        # Log training run to database
        try:
            db = SessionLocal()
            repo = TrainingRunRepository(db)
            run = TrainingRun(
                run_name=f"Run_{model_name}_{epochs}ep",
                model_architecture=str(model_name),
                optimizer=str(optimizer_name),
                loss_function=str(loss_name),
                epochs=epochs,
                batch_size=batch_size,
                learning_rate=lr,
                best_accuracy=max(history.get("accuracy", [0.0])),
                best_f1=max(history.get("f1_score", [0.0])),
                best_iou=max(history.get("iou", [0.0])),
                metrics_history=history
            )
            repo.create(run)
            db.close()
        except Exception as e:
            logger.warning(f"Failed to record training run in database: {e}")

        return history
