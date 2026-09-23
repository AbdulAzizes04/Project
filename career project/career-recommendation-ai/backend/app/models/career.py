from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class CareerRole(Base):
    __tablename__ = "career_roles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), unique=True, index=True, nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    min_cgpa = Column(Float, default=6.00)
    min_tenth_pct = Column(Float, default=60.00)
    min_twelfth_pct = Column(Float, default=60.00)
    min_aptitude_score = Column(Float, default=60.00)
    difficulty_level = Column(String(20), default="ENTRY")  # ENTRY, INTERMEDIATE, ADVANCED
    salary_range = Column(String(100), nullable=True)
    market_demand = Column(String(50), default="HIGH")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    career_skills = relationship("CareerSkill", back_populates="career", cascade="all, delete-orphan")
    career_certifications = relationship("CareerCertification", back_populates="career", cascade="all, delete-orphan")
    career_projects = relationship("CareerProject", back_populates="career", cascade="all, delete-orphan")
    recommendations = relationship("CareerRecommendation", back_populates="career", cascade="all, delete-orphan")
    skill_gaps = relationship("SkillGap", back_populates="career", cascade="all, delete-orphan")


class CareerSkill(Base):
    __tablename__ = "career_skills"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    career_id = Column(Integer, ForeignKey("career_roles.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    importance_weight = Column(Float, default=1.00, nullable=False)  # 1.0 to 5.0
    is_required = Column(Boolean, default=True, nullable=False)       # True = Required, False = Preferred
    min_proficiency = Column(String(20), default="INTERMEDIATE")     # BEGINNER, INTERMEDIATE, ADVANCED
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("career_id", "skill_id", name="uq_career_skill"),
    )

    career = relationship("CareerRole", back_populates="career_skills")
    skill = relationship("Skill", back_populates="career_skills")


class CareerCertification(Base):
    __tablename__ = "career_certifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    career_id = Column(Integer, ForeignKey("career_roles.id", ondelete="CASCADE"), nullable=False, index=True)
    certification_name = Column(String(200), nullable=False)
    domain = Column(String(100), nullable=True)
    relevance_weight = Column(Float, default=1.00)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    career = relationship("CareerRole", back_populates="career_certifications")


class CareerProject(Base):
    __tablename__ = "career_projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    career_id = Column(Integer, ForeignKey("career_roles.id", ondelete="CASCADE"), nullable=False, index=True)
    project_type = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    suggested_tech = Column(JSON, nullable=True)
    relevance_weight = Column(Float, default=1.00)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    career = relationship("CareerRole", back_populates="career_projects")
