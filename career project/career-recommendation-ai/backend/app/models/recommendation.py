from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class CareerRecommendation(Base):
    __tablename__ = "career_recommendations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    career_id = Column(Integer, ForeignKey("career_roles.id", ondelete="CASCADE"), nullable=False, index=True)
    compatibility_score = Column(Float, nullable=False)  # 0.0 to 100.0%
    rank_order = Column(Integer, nullable=False)          # 1 to 5
    ml_confidence = Column(Float, default=0.0)
    skill_compatibility = Column(Float, default=0.0)
    academic_compatibility = Column(Float, default=0.0)
    project_compatibility = Column(Float, default=0.0)
    certification_compatibility = Column(Float, default=0.0)
    aptitude_compatibility = Column(Float, default=0.0)
    interest_compatibility = Column(Float, default=0.0)
    domain_compatibility = Column(Float, default=0.0)
    matching_skills = Column(JSON, nullable=True)         # ["Python", "Pandas", "SQL"]
    missing_skills = Column(JSON, nullable=True)          # ["Docker", "Kubernetes"]
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    student = relationship("StudentProfile", back_populates="recommendations")
    career = relationship("CareerRole", back_populates="recommendations")
    explanation = relationship("RecommendationExplanation", back_populates="recommendation", uselist=False, cascade="all, delete-orphan")


class RecommendationExplanation(Base):
    __tablename__ = "recommendation_explanations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recommendation_id = Column(Integer, ForeignKey("career_recommendations.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    shap_values = Column(JSON, nullable=True)           # [{"feature": "python", "contribution": 0.18, "value": 1}, ...]
    lime_values = Column(JSON, nullable=True)           # [{"feature": "python", "weight": 0.22, "direction": "POSITIVE"}, ...]
    top_positive_factors = Column(JSON, nullable=True)  # [{"feature": "JavaScript", "percentage": 18.0}, ...]
    top_negative_factors = Column(JSON, nullable=True)  # [{"feature": "Cloud", "percentage": -6.0}, ...]
    human_readable_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    recommendation = relationship("CareerRecommendation", back_populates="explanation")


class SkillGap(Base):
    __tablename__ = "skill_gaps"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    career_id = Column(Integer, ForeignKey("career_roles.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    gap_status = Column(String(20), nullable=False)        # STRONG, MODERATE, MISSING
    student_level = Column(String(20), default="NONE")     # NONE, BEGINNER, INTERMEDIATE, ADVANCED
    required_level = Column(String(20), default="INTERMEDIATE")
    learning_priority = Column(String(20), nullable=False) # HIGH, MEDIUM, LOW
    priority_score = Column(Float, default=0.0)            # 0.0 to 100.0
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("student_id", "career_id", "skill_id", name="uq_student_career_skill_gap"),
    )

    student = relationship("StudentProfile", back_populates="skill_gaps")
    career = relationship("CareerRole", back_populates="skill_gaps")
    skill = relationship("Skill")
