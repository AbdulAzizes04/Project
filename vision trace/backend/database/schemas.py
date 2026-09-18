"""
VisionTrace AI — Pydantic Schemas
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
from datetime import datetime


# ── Case ──────────────────────────────────────────────────────────────────────

class CaseCreate(BaseModel):
    case_name: str
    notes: Optional[str] = None


class CaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    case_name: str
    created_at: datetime
    status: str
    video_name: Optional[str]
    total_frames: int
    persons_tracked: int
    matches_found: int
    overall_confidence: float
    processing_time: float
    evidence_rating: str
    notes: Optional[str]


# ── Track ──────────────────────────────────────────────────────────────────────

class TrackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    case_id: int
    track_number: int
    first_seen: float
    last_seen: float
    duration: float
    avg_confidence: float
    appearance_count: int


# ── Detection ─────────────────────────────────────────────────────────────────

class DetectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    track_id: int
    timestamp: float
    frame_number: int
    confidence: float
    bounding_box: Optional[Any]


# ── Evidence ──────────────────────────────────────────────────────────────────

class EvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    case_id: int
    track_id: Optional[int]
    timestamp: float
    event_type: str
    confidence: float
    description: str


# ── Analysis Result ───────────────────────────────────────────────────────────

class AnalysisResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    case_id: int
    track_id: int
    reid_score: float
    gait_score: float
    clothing_score: float
    face_score: float
    final_score: float
    evidence_rating: str


# ── Chat ──────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    question: str
    case_id: Optional[int] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = []


# ── Analysis Run ──────────────────────────────────────────────────────────────

class AnalysisRunRequest(BaseModel):
    case_id: int
    similarity_threshold: float = 0.85
    fps: int = 2
    demo_mode: bool = False
    demo_scenario: Optional[str] = None


class ProcessingStatus(BaseModel):
    case_id: int
    status: str
    current_step: int
    total_steps: int
    step_name: str
    progress: float
    message: str
