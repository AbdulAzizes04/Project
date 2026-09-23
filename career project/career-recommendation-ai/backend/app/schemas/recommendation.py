from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# --------------- Career Role ---------------
class CareerRoleResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    min_cgpa: float
    difficulty_level: str
    salary_range: Optional[str] = None
    market_demand: str

    class Config:
        from_attributes = True


# --------------- Recommendation ---------------
class RecommendationSHAPFactor(BaseModel):
    feature: str
    contribution: float
    direction: str  # POSITIVE or NEGATIVE


class RecommendationExplanationResponse(BaseModel):
    shap_values: Optional[List[Dict[str, Any]]] = None
    lime_values: Optional[List[Dict[str, Any]]] = None
    top_positive_factors: Optional[List[Dict[str, Any]]] = None
    top_negative_factors: Optional[List[Dict[str, Any]]] = None
    human_readable_text: str


class CareerRecommendationResponse(BaseModel):
    id: int
    career_id: int
    career_name: str
    career_slug: str
    career_description: str
    compatibility_score: float
    rank_order: int
    ml_confidence: float
    skill_compatibility: float
    academic_compatibility: float
    project_compatibility: float
    certification_compatibility: float
    aptitude_compatibility: float
    interest_compatibility: float
    domain_compatibility: float
    matching_skills: Optional[List[str]] = None
    missing_skills: Optional[List[str]] = None
    generated_at: datetime
    explanation: Optional[RecommendationExplanationResponse] = None

    class Config:
        from_attributes = True


class GenerateRecommendationRequest(BaseModel):
    regenerate: bool = False


class CompareCareerRequest(BaseModel):
    career_ids: List[int]


# --------------- Skill Gap ---------------
class SkillGapItemResponse(BaseModel):
    skill_id: int
    skill_name: str
    skill_category: str
    gap_status: str      # STRONG, MODERATE, MISSING
    student_level: str
    required_level: str
    learning_priority: str
    priority_score: float


class SkillGapResponse(BaseModel):
    career_id: int
    career_name: str
    strong_skills: List[SkillGapItemResponse]
    moderate_skills: List[SkillGapItemResponse]
    missing_skills: List[SkillGapItemResponse]
    skill_coverage_percent: float
    total_required: int
    matched_required: int


# --------------- Progress ---------------
class ProgressCreate(BaseModel):
    item_type: str
    title: str
    week_number: int = 1
    skill_id: Optional[int] = None
    notes: Optional[str] = None


class ProgressUpdate(BaseModel):
    status: str
    progress_percent: int = 0
    notes: Optional[str] = None


class ProgressResponse(ProgressCreate):
    id: int
    student_id: int
    status: str
    progress_percent: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
