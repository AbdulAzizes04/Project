"""
Repository Pattern Implementation for EARTH VISION-X Database Access.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from earth_vision_x.app.database.models import PredictionRecord, TrainingRun, DatasetMetadata
from earth_vision_x.app.config.logging_config import logger

class PredictionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, record: PredictionRecord) -> PredictionRecord:
        """Saves a new prediction record."""
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        logger.info(f"Saved prediction record ID {record.id}")
        return record

    def get_all(self, limit: int = 50) -> List[PredictionRecord]:
        """Retrieves recent prediction records."""
        return self.db.query(PredictionRecord).order_by(PredictionRecord.timestamp.desc()).limit(limit).all()

    def get_by_id(self, record_id: int) -> Optional[PredictionRecord]:
        """Retrieves a single prediction by ID."""
        return self.db.query(PredictionRecord).filter(PredictionRecord.id == record_id).first()

class TrainingRunRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, run: TrainingRun) -> TrainingRun:
        """Saves a new training run record."""
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        logger.info(f"Saved training run ID {run.id}")
        return run

    def get_all(self, limit: int = 20) -> List[TrainingRun]:
        """Retrieves training runs."""
        return self.db.query(TrainingRun).order_by(TrainingRun.created_at.desc()).limit(limit).all()

class DatasetRepository:
    def __init__(self, db: Session):
        self.db = db

    def register_or_update(self, dataset: DatasetMetadata) -> DatasetMetadata:
        """Registers a new dataset or updates existing dataset metadata."""
        existing = self.db.query(DatasetMetadata).filter(DatasetMetadata.dataset_name == dataset.dataset_name).first()
        if existing:
            existing.num_samples = dataset.num_samples
            existing.sensor_type = dataset.sensor_type
            existing.spatial_resolution = dataset.spatial_resolution
            existing.crs = dataset.crs
            existing.description = dataset.description
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            self.db.add(dataset)
            self.db.commit()
            self.db.refresh(dataset)
            return dataset

    def get_all(self) -> List[DatasetMetadata]:
        return self.db.query(DatasetMetadata).all()
