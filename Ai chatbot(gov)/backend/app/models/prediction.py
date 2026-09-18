"""
AI prediction models:
- ComplaintPrediction: stores AI classification, priority, duplicate results
- ComplaintEmbedding: stores sentence-transformer vector for duplicate detection
- ModelEvaluation: stores actual model performance metrics (accuracy, F1, etc.)
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Text, Float, Integer, JSON
from app.core.database import Base


class ComplaintPrediction(Base):
    __tablename__ = "complaint_predictions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    complaint_id = Column(String(36), nullable=False, unique=True, index=True)

    # Classification
    predicted_category = Column(String(100), nullable=True)
    category_confidence = Column(Float, nullable=True)

    # Priority
    predicted_priority = Column(String(50), nullable=True)
    priority_confidence = Column(Float, nullable=True)

    # Duplicate detection
    is_duplicate = Column(Boolean, default=False)
    duplicate_similarity = Column(Float, nullable=True)
    duplicate_complaint_id = Column(String(36), nullable=True)
    duplicate_complaint_number = Column(String(50), nullable=True)

    # Department recommendation (DB-driven)
    recommended_department_id = Column(String(36), nullable=True)
    recommended_department_name = Column(String(255), nullable=True)

    # Model metadata
    model_version = Column(String(50), nullable=True, default="1.0.0")
    low_confidence_flag = Column(Boolean, default=False)

    # Admin corrections (stored for future retraining)
    admin_corrected_category = Column(String(100), nullable=True)
    admin_corrected_priority = Column(String(50), nullable=True)

    # Full raw analysis output (JSON)
    raw_analysis = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class ComplaintEmbedding(Base):
    __tablename__ = "complaint_embeddings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    complaint_id = Column(String(36), nullable=False, unique=True, index=True)
    # Stored as JSON array of floats
    embedding = Column(JSON, nullable=False)
    model_name = Column(String(100), nullable=False, default="all-MiniLM-L6-v2")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ModelEvaluation(Base):
    __tablename__ = "model_evaluations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_name = Column(String(100), nullable=False)
    model_type = Column(String(100), nullable=False)  # classifier | priority
    algorithm = Column(String(100), nullable=True)

    # Core metrics (stored from actual evaluation, NEVER hard-coded)
    accuracy = Column(Float, nullable=True)
    precision_score = Column(Float, nullable=True)
    recall_score = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)

    # Detailed results
    confusion_matrix = Column(JSON, nullable=True)    # 2D list
    classification_report = Column(JSON, nullable=True)
    label_names = Column(JSON, nullable=True)          # List of class names

    # Dataset info
    dataset_size = Column(Integer, nullable=True)
    train_size = Column(Integer, nullable=True)
    test_size = Column(Integer, nullable=True)
    train_accuracy = Column(Float, nullable=True)

    is_active = Column(Boolean, default=True)  # The currently deployed model
    evaluated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
