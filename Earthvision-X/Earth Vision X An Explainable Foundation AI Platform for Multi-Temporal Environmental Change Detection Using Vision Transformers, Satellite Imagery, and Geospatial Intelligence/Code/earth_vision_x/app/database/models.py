"""
Database Models (ORM) for Prediction History, Training Runs, and Datasets.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from earth_vision_x.app.database.db import Base

class PredictionRecord(Base):
    __tablename__ = "prediction_records"

    id = Column(Integer, primary_key=True, index=True)
    t1_filename = Column(String(255), nullable=False)
    t2_filename = Column(String(255), nullable=False)
    model_used = Column(String(100), nullable=False)
    primary_change_detected = Column(String(100), nullable=False)
    confidence_score = Column(Float, nullable=False)
    affected_area_sqkm = Column(Float, nullable=False)
    affected_percentage = Column(Float, nullable=False)
    ai_explanation = Column(Text, nullable=True)
    heatmap_path = Column(String(500), nullable=True)
    report_pdf_path = Column(String(500), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class TrainingRun(Base):
    __tablename__ = "training_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_name = Column(String(100), nullable=False)
    model_architecture = Column(String(100), nullable=False)
    optimizer = Column(String(50), nullable=False)
    loss_function = Column(String(50), nullable=False)
    epochs = Column(Integer, nullable=False)
    batch_size = Column(Integer, nullable=False)
    learning_rate = Column(Float, nullable=False)
    best_accuracy = Column(Float, nullable=True)
    best_f1 = Column(Float, nullable=True)
    best_iou = Column(Float, nullable=True)
    metrics_history = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DatasetMetadata(Base):
    __tablename__ = "dataset_metadata"

    id = Column(Integer, primary_key=True, index=True)
    dataset_name = Column(String(100), nullable=False, unique=True)
    sensor_type = Column(String(50), nullable=False) # e.g. Sentinel-2, Landsat
    num_samples = Column(Integer, default=0)
    spatial_resolution = Column(String(50), default="10m")
    crs = Column(String(50), default="EPSG:4326")
    description = Column(Text, nullable=True)
    registered_at = Column(DateTime, default=datetime.utcnow)
