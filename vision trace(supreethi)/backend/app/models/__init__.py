import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Text, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.database.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255))
    badge_number = Column(String(100))
    department = Column(String(255))
    role = Column(String(50), default="Investigator")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(String(36), primary_key=True)
    case_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    status = Column(String(50), default="Pending") # Pending, Processing, Completed, Failed
    priority = Column(String(20), default="High")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    incident = relationship("IncidentDetails", back_populates="investigation", uselist=False, cascade="all, delete-orphan")
    videos = relationship("Video", back_populates="investigation", cascade="all, delete-orphan")
    reference_images = relationship("ReferenceImage", back_populates="investigation", cascade="all, delete-orphan")
    detected_persons = relationship("DetectedPerson", back_populates="investigation", cascade="all, delete-orphan")
    timeline_events = relationship("TimelineEvent", back_populates="investigation", cascade="all, delete-orphan")
    evidence_items = relationship("EvidenceItem", back_populates="investigation", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="investigation", cascade="all, delete-orphan")
    processing_jobs = relationship("ProcessingJob", back_populates="investigation", cascade="all, delete-orphan")

class IncidentDetails(Base):
    __tablename__ = "incident_details"

    id = Column(String(36), primary_key=True)
    investigation_id = Column(String(36), ForeignKey("investigations.id"), nullable=False)
    incident_type = Column(String(100), nullable=False) # Theft, Robbery, Assault, etc.
    incident_date = Column(String(50), nullable=False)
    incident_time = Column(String(50), nullable=False)
    location = Column(String(255), nullable=False)
    police_station = Column(String(255), nullable=False)
    investigator_name = Column(String(255), nullable=False)
    case_description = Column(Text, nullable=True)

    investigation = relationship("Investigation", back_populates="incident")

class Video(Base):
    __tablename__ = "videos"

    id = Column(String(36), primary_key=True)
    investigation_id = Column(String(36), ForeignKey("investigations.id"), nullable=False)
    camera_id = Column(String(100), nullable=False) # Camera 01, North Gate, etc.
    location = Column(String(255))
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    duration_seconds = Column(Float, default=0.0)
    resolution = Column(String(50), default="1920x1080")
    fps = Column(Float, default=30.0)
    file_size_mb = Column(Float, default=0.0)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    investigation = relationship("Investigation", back_populates="videos")
    detected_persons = relationship("DetectedPerson", back_populates="video")

class ReferenceImage(Base):
    __tablename__ = "reference_images"

    id = Column(String(36), primary_key=True)
    investigation_id = Column(String(36), ForeignKey("investigations.id"), nullable=False)
    image_type = Column(String(50), default="Suspect") # Suspect, Victim, Both
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    feature_vector = Column(JSON, nullable=True) # Extracted embedding vector
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    investigation = relationship("Investigation", back_populates="reference_images")

class DetectedPerson(Base):
    __tablename__ = "detected_persons"

    id = Column(String(36), primary_key=True)
    investigation_id = Column(String(36), ForeignKey("investigations.id"), nullable=False)
    video_id = Column(String(36), ForeignKey("videos.id"), nullable=True)
    track_id = Column(Integer, nullable=False, index=True) # E.g. 7
    label = Column(String(100), default="Candidate Person of Interest")
    confidence_score = Column(Float, default=0.90)
    similarity_score = Column(Float, default=0.0) # Cosine similarity with reference image
    ai_relevance_score = Column(Float, default=0.85)
    face_visibility = Column(String(50), default="Visible") # Visible, Masked, Partially Covered, Occluded
    alternative_pipeline_active = Column(Boolean, default=False)
    first_seen = Column(String(50))
    last_seen = Column(String(50))
    total_duration = Column(String(50))
    camera_locations = Column(JSON, default=list) # ["Camera 01 - Main Entrance", "Camera 02 - Vault Corridor"]
    appearance_description = Column(Text) # E.g. "Dark hooded jacket, dark denim jeans, athletic sneakers"
    clothing_upper = Column(String(100))
    clothing_lower = Column(String(100))
    snapshot_url = Column(String(500))
    is_person_of_interest = Column(Boolean, default=True)

    investigation = relationship("Investigation", back_populates="detected_persons")
    video = relationship("Video", back_populates="detected_persons")
    tracks = relationship("PersonTrack", back_populates="person", cascade="all, delete-orphan")
    gait_profile = relationship("GaitAnalysis", back_populates="person", uselist=False, cascade="all, delete-orphan")

class PersonTrack(Base):
    __tablename__ = "person_tracks"

    id = Column(String(36), primary_key=True)
    detected_person_id = Column(String(36), ForeignKey("detected_persons.id"), nullable=False)
    frame_number = Column(Integer, nullable=False)
    timestamp = Column(String(50), nullable=False)
    bbox_x = Column(Float, nullable=False)
    bbox_y = Column(Float, nullable=False)
    bbox_w = Column(Float, nullable=False)
    bbox_h = Column(Float, nullable=False)
    confidence = Column(Float, default=0.9)
    camera_id = Column(String(100))

    person = relationship("DetectedPerson", back_populates="tracks")

class GaitAnalysis(Base):
    __tablename__ = "gait_analysis"

    id = Column(String(36), primary_key=True)
    detected_person_id = Column(String(36), ForeignKey("detected_persons.id"), nullable=False)
    track_id = Column(Integer, nullable=False)
    walking_speed = Column(String(50), default="Moderate (1.3 m/s)")
    stride_pattern = Column(String(50), default="Regular asymmetric left-bias")
    step_frequency = Column(String(50), default="108 steps/min")
    arm_swing = Column(String(50), default="Low / Restricted")
    leg_movement = Column(String(50), default="Normal Knee Flexion")
    body_posture = Column(String(100), default="Slight Forward Lean (7°)")
    gait_signature = Column(String(100), default="GAIT-007")
    cadence_score = Column(Float, default=0.82)
    stride_symmetry = Column(Float, default=0.74)
    arm_swing_amplitude = Column(Float, default=0.35)
    keypoint_summary = Column(JSON, default=dict)

    person = relationship("DetectedPerson", back_populates="gait_profile")

class EvidenceItem(Base):
    __tablename__ = "evidence_items"

    id = Column(String(36), primary_key=True)
    investigation_id = Column(String(36), ForeignKey("investigations.id"), nullable=False)
    title = Column(String(255), nullable=False)
    category = Column(String(100), default="Person Appearance") # Person Appearance, Suspicious Activity, Vehicle, Low-Light Enhancement
    timestamp = Column(String(50))
    camera_id = Column(String(100))
    frame_url = Column(String(500))
    clip_url = Column(String(500))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    investigation = relationship("Investigation", back_populates="evidence_items")

class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id = Column(String(36), primary_key=True)
    investigation_id = Column(String(36), ForeignKey("investigations.id"), nullable=False)
    timestamp = Column(String(50), nullable=False)
    camera_id = Column(String(100), nullable=False)
    event_type = Column(String(100), nullable=False) # First Detected, Movement, Activity, Last Recorded
    description = Column(Text, nullable=False)
    relevance_level = Column(String(20), default="High")
    track_id = Column(Integer, nullable=True)
    thumbnail_url = Column(String(500), nullable=True)

    investigation = relationship("Investigation", back_populates="timeline_events")

class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True)
    investigation_id = Column(String(36), ForeignKey("investigations.id"), nullable=False)
    report_number = Column(String(100), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    pdf_path = Column(String(500), nullable=True)
    executive_summary = Column(Text)
    ai_findings = Column(JSON)
    disclaimer = Column(Text, default=(
        "This report contains AI-assisted analytical results generated by VisionTrace AI. "
        "All findings require independent verification by authorized human investigators. "
        "AI-generated similarity and relevance scores must not be treated as definitive proof of identity or criminal guilt."
    ))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    investigation = relationship("Investigation", back_populates="reports")

class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(String(36), primary_key=True)
    investigation_id = Column(String(36), ForeignKey("investigations.id"), nullable=False)
    status = Column(String(50), default="QUEUED") # QUEUED, PROCESSING, COMPLETED, FAILED
    progress_percentage = Column(Integer, default=0)
    current_step = Column(String(255), default="Initializing analysis engine...")
    logs = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    investigation = relationship("Investigation", back_populates="processing_jobs")
