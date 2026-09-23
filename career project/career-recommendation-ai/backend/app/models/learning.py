from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class LearningResource(Base):
    __tablename__ = "learning_resources"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(250), nullable=False)
    resource_type = Column(String(50), default="COURSE")  # COURSE, DOCUMENTATION, BOOK, TUTORIAL, PROJECT
    platform = Column(String(100), nullable=True)         # Coursera, Udemy, YouTube, FreeCodeCamp
    url = Column(String(500), nullable=False)
    estimated_hours = Column(Integer, default=10)
    difficulty = Column(String(20), default="BEGINNER")    # BEGINNER, INTERMEDIATE, ADVANCED
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    skill = relationship("Skill", back_populates="learning_resources")


class StudentProgress(Base):
    __tablename__ = "student_progress"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="SET NULL"), nullable=True, index=True)
    item_type = Column(String(50), nullable=False)        # SKILL, COURSE, PROJECT, CERTIFICATION, MILESTONE
    title = Column(String(250), nullable=False)
    week_number = Column(Integer, default=1)
    status = Column(String(20), default="NOT_STARTED")    # NOT_STARTED, LEARNING, COMPLETED
    progress_percent = Column(Integer, default=0)         # 0 to 100
    notes = Column(Text, nullable=True)
    target_completion_date = Column(Date, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    student = relationship("StudentProfile", back_populates="progress_items")
    skill = relationship("Skill")
