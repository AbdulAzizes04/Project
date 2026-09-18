"""Pydantic schemas for analytics responses."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class CategoryStat(BaseModel):
    category: str
    count: int
    percentage: float


class PriorityStat(BaseModel):
    priority: str
    count: int
    percentage: float


class StatusStat(BaseModel):
    status: str
    count: int
    percentage: float


class DepartmentStat(BaseModel):
    department_id: str
    department_name: str
    total: int
    resolved: int
    pending: int
    avg_resolution_hours: Optional[float] = None


class TimelineStat(BaseModel):
    date: str
    count: int


class DashboardStats(BaseModel):
    total_complaints: int
    pending: int
    in_progress: int
    resolved: int
    closed: int
    critical: int
    possible_duplicates: int
    verified: int
    unverified: int
    total_citizens: int
    total_departments: int
    complaints_today: int
    resolution_rate: float  # percentage


class ModelMetrics(BaseModel):
    model_name: str
    model_type: str
    algorithm: Optional[str]
    accuracy: Optional[float]
    precision_score: Optional[float]
    recall_score: Optional[float]
    f1_score: Optional[float]
    train_accuracy: Optional[float]
    dataset_size: Optional[int]
    confusion_matrix: Optional[List[List[int]]]
    classification_report: Optional[Dict[str, Any]]
    label_names: Optional[List[str]]
    evaluated_at: Optional[datetime]
    is_active: bool


class AnalyticsResponse(BaseModel):
    success: bool = True
    data: Any
