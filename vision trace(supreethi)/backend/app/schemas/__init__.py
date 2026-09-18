from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class IncidentDetailsBase(BaseModel):
    incident_type: str = "Theft"
    incident_date: str
    incident_time: str
    location: str
    police_station: str
    investigator_name: str
    case_description: Optional[str] = None

class IncidentDetailsCreate(IncidentDetailsBase):
    pass

class IncidentDetailsResponse(IncidentDetailsBase):
    id: str
    investigation_id: str

    class Config:
        from_attributes = True

class InvestigationCreate(BaseModel):
    case_id: str
    title: str
    priority: str = "High"
    incident: IncidentDetailsCreate

class VideoResponse(BaseModel):
    id: str
    camera_id: str
    location: Optional[str]
    filename: str
    filepath: str
    duration_seconds: float
    resolution: str
    fps: float
    file_size_mb: float
    processed: bool

    class Config:
        from_attributes = True

class ReferenceImageResponse(BaseModel):
    id: str
    image_type: str
    filename: str
    filepath: str

    class Config:
        from_attributes = True

class GaitAnalysisResponse(BaseModel):
    id: str
    track_id: int
    walking_speed: str
    stride_pattern: str
    step_frequency: str
    arm_swing: str
    leg_movement: str
    body_posture: str
    gait_signature: str
    cadence_score: float
    stride_symmetry: float
    arm_swing_amplitude: float
    keypoint_summary: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class PersonTrackResponse(BaseModel):
    id: str
    frame_number: int
    timestamp: str
    bbox_x: float
    bbox_y: float
    bbox_w: float
    bbox_h: float
    confidence: float
    camera_id: Optional[str]

    class Config:
        from_attributes = True

class DetectedPersonResponse(BaseModel):
    id: str
    track_id: int
    label: str
    confidence_score: float
    similarity_score: float
    ai_relevance_score: float
    face_visibility: str
    alternative_pipeline_active: bool
    first_seen: Optional[str]
    last_seen: Optional[str]
    total_duration: Optional[str]
    camera_locations: List[str] = []
    appearance_description: Optional[str]
    clothing_upper: Optional[str]
    clothing_lower: Optional[str]
    snapshot_url: Optional[str]
    is_person_of_interest: bool
    gait_profile: Optional[GaitAnalysisResponse] = None

    class Config:
        from_attributes = True

class TimelineEventResponse(BaseModel):
    id: str
    timestamp: str
    camera_id: str
    event_type: str
    description: str
    relevance_level: str
    track_id: Optional[int] = None
    thumbnail_url: Optional[str] = None

    class Config:
        from_attributes = True

class EvidenceItemCreate(BaseModel):
    title: str
    category: str = "Person Appearance"
    timestamp: Optional[str] = None
    camera_id: Optional[str] = None
    notes: Optional[str] = None

class EvidenceItemResponse(BaseModel):
    id: str
    investigation_id: str
    title: str
    category: str
    timestamp: Optional[str]
    camera_id: Optional[str]
    frame_url: Optional[str]
    clip_url: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ReportResponse(BaseModel):
    id: str
    investigation_id: str
    report_number: str
    title: str
    pdf_path: Optional[str]
    executive_summary: Optional[str]
    ai_findings: Optional[Dict[str, Any]]
    disclaimer: str
    created_at: datetime

    class Config:
        from_attributes = True

class ProcessingJobResponse(BaseModel):
    id: str
    investigation_id: str
    status: str
    progress_percentage: int
    current_step: str
    logs: List[str] = []

    class Config:
        from_attributes = True

class InvestigationResponse(BaseModel):
    id: str
    case_id: str
    title: str
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime
    incident: Optional[IncidentDetailsResponse] = None
    videos: List[VideoResponse] = []
    reference_images: List[ReferenceImageResponse] = []
    detected_persons: List[DetectedPersonResponse] = []
    timeline_events: List[TimelineEventResponse] = []
    evidence_items: List[EvidenceItemResponse] = []
    reports: List[ReportResponse] = []

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    active_investigations: int
    total_videos_processed: int
    persons_detected: int
    evidence_items: int
    reports_generated: int
    recent_investigations: List[Dict[str, Any]]

class NLPSearchRequest(BaseModel):
    query: str
    investigation_id: Optional[str] = None

class NLPSearchResult(BaseModel):
    parsed_filters: Dict[str, Any]
    matched_persons: List[DetectedPersonResponse]
    matched_events: List[TimelineEventResponse]
    matched_videos: List[VideoResponse]

class ANPRPlateResult(BaseModel):
    plate_number: str
    vehicle_type: str
    confidence: float
    timestamp: str
    camera_id: str
    image_url: Optional[str] = None
