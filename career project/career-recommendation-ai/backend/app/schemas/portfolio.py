from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


# --------------- Skills ---------------
class SkillResponse(BaseModel):
    id: int
    name: str
    category: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class StudentSkillCreate(BaseModel):
    skill_id: int
    proficiency_level: str = "INTERMEDIATE"


class StudentSkillUpdate(BaseModel):
    proficiency_level: str


class StudentSkillResponse(BaseModel):
    id: int
    skill_id: int
    skill_name: str
    skill_category: str
    proficiency_level: str
    verified: bool

    class Config:
        from_attributes = True


# --------------- Certifications ---------------
class CertificationCreate(BaseModel):
    certification_name: str
    issuer: str
    issue_date: Optional[date] = None
    domain: Optional[str] = None
    verification_url: Optional[str] = None


class CertificationUpdate(CertificationCreate):
    pass


class CertificationResponse(CertificationCreate):
    id: int
    student_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# --------------- Projects ---------------
class ProjectCreate(BaseModel):
    project_name: str
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
    domain: Optional[str] = None
    complexity: str = "MEDIUM"
    role: Optional[str] = None
    duration_months: int = 1
    project_url: Optional[str] = None


class ProjectUpdate(ProjectCreate):
    pass


class ProjectResponse(ProjectCreate):
    id: int
    student_id: int
    created_at: datetime

    class Config:
        from_attributes = True
