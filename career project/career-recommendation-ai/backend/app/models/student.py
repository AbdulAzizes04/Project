from sqlalchemy import Column, Integer, String, Float, Text, Date, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    phone = Column(String(20), nullable=True)
    location = Column(String(100), nullable=True)
    batch = Column(String(50), nullable=True)  # e.g., "2023-2027"
    branch = Column(String(100), nullable=True)  # e.g., "Artificial Intelligence and Data Science"
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="student_profile")
    academic_record = relationship("AcademicRecord", back_populates="student", uselist=False, cascade="all, delete-orphan")
    aptitude_score = relationship("AptitudeScore", back_populates="student", uselist=False, cascade="all, delete-orphan")
    career_interest = relationship("CareerInterest", back_populates="student", uselist=False, cascade="all, delete-orphan")
    skills = relationship("StudentSkill", back_populates="student", cascade="all, delete-orphan")
    certifications = relationship("StudentCertification", back_populates="student", cascade="all, delete-orphan")
    projects = relationship("StudentProject", back_populates="student", cascade="all, delete-orphan")
    recommendations = relationship("CareerRecommendation", back_populates="student", cascade="all, delete-orphan")
    skill_gaps = relationship("SkillGap", back_populates="student", cascade="all, delete-orphan")
    progress_items = relationship("StudentProgress", back_populates="student", cascade="all, delete-orphan")


class AcademicRecord(Base):
    __tablename__ = "academic_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    tenth_percentage = Column(Float, nullable=True)
    twelfth_percentage = Column(Float, nullable=True)
    cgpa = Column(Float, nullable=True)
    semester_scores = Column(JSON, nullable=True)  # {"sem1": 8.5, "sem2": 8.7, ...}
    core_subject_performance = Column(JSON, nullable=True)  # {"dsa": 88, "dbms": 90, "python": 92}
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    student = relationship("StudentProfile", back_populates="academic_record")


class AptitudeScore(Base):
    __tablename__ = "aptitude_scores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    quantitative_score = Column(Float, default=0.0)
    logical_reasoning_score = Column(Float, default=0.0)
    verbal_score = Column(Float, default=0.0)
    technical_aptitude_score = Column(Float, default=0.0)
    total_score = Column(Float, default=0.0)
    assessment_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    student = relationship("StudentProfile", back_populates="aptitude_score")


class CareerInterest(Base):
    __tablename__ = "career_interests"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    preferred_domains = Column(JSON, nullable=True)       # ["Artificial Intelligence", "Web Development"]
    career_interests = Column(JSON, nullable=True)        # ["AI/ML Engineer", "Data Scientist"]
    preferred_technologies = Column(JSON, nullable=True)  # ["Python", "PyTorch", "FastAPI"]
    soft_skills = Column(JSON, nullable=True)             # {"communication": 4, "leadership": 3, "teamwork": 5, "problem_solving": 4}
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    student = relationship("StudentProfile", back_populates="career_interest")
