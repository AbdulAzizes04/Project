"""
VisionTrace AI — SQLAlchemy ORM Models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database.database import Base


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    case_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String, default="pending")  # pending | processing | completed | error
    video_path = Column(String, nullable=True)
    video_name = Column(String, nullable=True)
    reference_image_path = Column(String, nullable=True)
    total_frames = Column(Integer, default=0)
    persons_tracked = Column(Integer, default=0)
    matches_found = Column(Integer, default=0)
    overall_confidence = Column(Float, default=0.0)
    processing_time = Column(Float, default=0.0)
    evidence_rating = Column(String, default="LOW")
    notes = Column(Text, nullable=True)

    tracks = relationship("Track", back_populates="case", cascade="all, delete")
    evidence = relationship("Evidence", back_populates="case", cascade="all, delete")
    analysis_results = relationship("AnalysisResult", back_populates="case", cascade="all, delete")
    chat_history = relationship("ChatHistory", back_populates="case", cascade="all, delete")


class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    track_number = Column(Integer, nullable=False)
    first_seen = Column(Float, default=0.0)   # seconds
    last_seen = Column(Float, default=0.0)
    duration = Column(Float, default=0.0)
    avg_confidence = Column(Float, default=0.0)
    appearance_count = Column(Integer, default=0)

    case = relationship("Case", back_populates="tracks")
    detections = relationship("Detection", back_populates="track", cascade="all, delete")
    analysis_result = relationship("AnalysisResult", back_populates="track", cascade="all, delete")


class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    timestamp = Column(Float, nullable=False)
    frame_number = Column(Integer, nullable=False)
    confidence = Column(Float, default=0.0)
    bounding_box = Column(JSON, nullable=True)  # [x1, y1, x2, y2]

    track = relationship("Track", back_populates="detections")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    track_id = Column(Integer, nullable=True)
    timestamp = Column(Float, nullable=False)
    event_type = Column(String, nullable=False)
    confidence = Column(Float, default=0.0)
    description = Column(Text, nullable=False)

    case = relationship("Case", back_populates="evidence")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    reid_score = Column(Float, default=0.0)
    gait_score = Column(Float, default=0.0)
    clothing_score = Column(Float, default=0.0)
    face_score = Column(Float, default=0.0)
    final_score = Column(Float, default=0.0)
    evidence_rating = Column(String, default="LOW")

    case = relationship("Case", back_populates="analysis_results")
    track = relationship("Track", back_populates="analysis_result")


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    case = relationship("Case", back_populates="chat_history")
