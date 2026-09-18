"""
Data Models for BuildVerse AI
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class RoomModel(BaseModel):
    id: Optional[int] = None
    floor_id: Optional[int] = None
    project_id: Optional[int] = None
    room_type: str
    length: float
    width: float
    area: float
    position: str = "Center"
    windows: int = 1
    doors: int = 1

class FloorModel(BaseModel):
    id: Optional[int] = None
    project_id: Optional[int] = None
    floor_name: str
    floor_level: int
    rooms: List[RoomModel] = []

class SchedulePhaseModel(BaseModel):
    id: Optional[int] = None
    project_id: Optional[int] = None
    phase_name: str
    start_date: str
    end_date: str
    duration_days: int
    progress_pct: float = 0.0
    cost: float = 0.0
    labor: int = 5
    materials: str = ""
    dependencies: str = ""
    status: str = "Pending"

class ProjectModel(BaseModel):
    id: Optional[int] = None
    name: str
    owner_name: str
    location: str
    plot_area: float
    plot_unit: str = "sq.ft"
    budget: float
    num_floors: int = 1
    start_date: Optional[str] = None
    completion_date: Optional[str] = None
    workers_available: int = 10
    working_hours_per_day: float = 8.0
    material_preference: str = "Standard"
    weather_region: str = "Moderate"
    floors: List[FloorModel] = []
    schedules: List[SchedulePhaseModel] = []

class MonitoringLogModel(BaseModel):
    id: Optional[int] = None
    project_id: int
    log_date: str
    media_path: Optional[str] = None
    media_type: Optional[str] = "image"
    completed_work_pct: float
    missing_work_pct: float
    overall_progress_pct: float
    delay_pct: float
    quality_score: float
    status: str
    ai_summary: str
    ai_recommendation: str
