from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# --------------- Student Profile ---------------
class StudentProfileBase(BaseModel):
    name: str
    phone: Optional[str] = None
    location: Optional[str] = None
    batch: Optional[str] = None
    branch: Optional[str] = None
    bio: Optional[str] = None


class StudentProfileCreate(StudentProfileBase):
    pass


class StudentProfileResponse(StudentProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --------------- Academic Records ---------------
class AcademicRecordBase(BaseModel):
    tenth_percentage: Optional[float] = None
    twelfth_percentage: Optional[float] = None
    cgpa: Optional[float] = None
    semester_scores: Optional[Dict[str, float]] = None
    core_subject_performance: Optional[Dict[str, float]] = None


class AcademicRecordCreate(AcademicRecordBase):
    pass


class AcademicRecordResponse(AcademicRecordBase):
    id: int
    student_id: int
    updated_at: datetime

    class Config:
        from_attributes = True


# --------------- Aptitude Scores ---------------
class AptitudeScoreBase(BaseModel):
    quantitative_score: Optional[float] = 0.0
    logical_reasoning_score: Optional[float] = 0.0
    verbal_score: Optional[float] = 0.0
    technical_aptitude_score: Optional[float] = 0.0


class AptitudeScoreCreate(AptitudeScoreBase):
    pass


class AptitudeScoreResponse(AptitudeScoreBase):
    id: int
    student_id: int
    total_score: float
    updated_at: datetime

    class Config:
        from_attributes = True


# --------------- Career Interests ---------------
class CareerInterestBase(BaseModel):
    preferred_domains: Optional[List[str]] = None
    career_interests: Optional[List[str]] = None
    preferred_technologies: Optional[List[str]] = None
    soft_skills: Optional[Dict[str, int]] = None


class CareerInterestCreate(CareerInterestBase):
    pass


class CareerInterestResponse(CareerInterestBase):
    id: int
    student_id: int
    updated_at: datetime

    class Config:
        from_attributes = True


# --------------- Full Profile with Completion ---------------
class ProfileCompletionSection(BaseModel):
    section: str
    completed: bool
    score: int


class FullStudentProfileResponse(BaseModel):
    profile: Optional[StudentProfileResponse] = None
    academic: Optional[AcademicRecordResponse] = None
    aptitude: Optional[AptitudeScoreResponse] = None
    interests: Optional[CareerInterestResponse] = None
    skills_count: int = 0
    certifications_count: int = 0
    projects_count: int = 0
    completion_percentage: float = 0.0
    completion_sections: List[ProfileCompletionSection] = []
