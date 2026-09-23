from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.student import StudentProfile
from app.models.skill import Skill, StudentSkill, SkillAlias
from app.models.portfolio import StudentCertification, StudentProject
from app.schemas.portfolio import (
    StudentSkillCreate, StudentSkillUpdate, StudentSkillResponse,
    CertificationCreate, CertificationUpdate, CertificationResponse,
    ProjectCreate, ProjectUpdate, ProjectResponse, SkillResponse
)
from app.middleware.auth_middleware import require_student

router = APIRouter(tags=["Student Portfolio"])


def _resolve_skill_name(name: str, db: Session) -> Skill | None:
    """Resolve raw skill name using alias map for normalization."""
    skill = db.query(Skill).filter(Skill.name.ilike(name)).first()
    if skill:
        return skill
    alias = db.query(SkillAlias).filter(SkillAlias.alias.ilike(name)).first()
    if alias:
        return alias.skill
    return None


def _get_profile(user: User, db: Session) -> StudentProfile:
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found.")
    return profile


# =================== SKILLS ===================
@router.get("/student/skills", response_model=List[StudentSkillResponse])
def get_skills(current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    profile = _get_profile(current_user, db)
    rows = db.query(StudentSkill).filter(StudentSkill.student_id == profile.id).all()
    return [
        StudentSkillResponse(
            id=r.id, skill_id=r.skill_id,
            skill_name=r.skill.name, skill_category=r.skill.category,
            proficiency_level=r.proficiency_level, verified=r.verified
        )
        for r in rows
    ]


@router.post("/student/skills", response_model=StudentSkillResponse, status_code=201)
def add_skill(payload: StudentSkillCreate, current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    profile = _get_profile(current_user, db)
    skill = db.query(Skill).filter(Skill.id == payload.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found in catalog.")
    existing = db.query(StudentSkill).filter(
        StudentSkill.student_id == profile.id,
        StudentSkill.skill_id == payload.skill_id
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Skill already added to your profile.")
    ss = StudentSkill(student_id=profile.id, skill_id=payload.skill_id, proficiency_level=payload.proficiency_level)
    db.add(ss)
    db.commit()
    db.refresh(ss)
    return StudentSkillResponse(id=ss.id, skill_id=ss.skill_id, skill_name=skill.name, skill_category=skill.category, proficiency_level=ss.proficiency_level, verified=ss.verified)


@router.put("/student/skills/{skill_entry_id}", response_model=StudentSkillResponse)
def update_skill(skill_entry_id: int, payload: StudentSkillUpdate, current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    profile = _get_profile(current_user, db)
    ss = db.query(StudentSkill).filter(StudentSkill.id == skill_entry_id, StudentSkill.student_id == profile.id).first()
    if not ss:
        raise HTTPException(status_code=404, detail="Skill entry not found.")
    ss.proficiency_level = payload.proficiency_level
    db.commit()
    db.refresh(ss)
    return StudentSkillResponse(id=ss.id, skill_id=ss.skill_id, skill_name=ss.skill.name, skill_category=ss.skill.category, proficiency_level=ss.proficiency_level, verified=ss.verified)


@router.delete("/student/skills/{skill_entry_id}", status_code=204)
def delete_skill(skill_entry_id: int, current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    profile = _get_profile(current_user, db)
    ss = db.query(StudentSkill).filter(StudentSkill.id == skill_entry_id, StudentSkill.student_id == profile.id).first()
    if not ss:
        raise HTTPException(status_code=404, detail="Skill entry not found.")
    db.delete(ss)
    db.commit()


# =================== CERTIFICATIONS ===================
@router.get("/student/certifications", response_model=List[CertificationResponse])
def get_certs(current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    profile = _get_profile(current_user, db)
    return db.query(StudentCertification).filter(StudentCertification.student_id == profile.id).all()


@router.post("/student/certifications", response_model=CertificationResponse, status_code=201)
def add_cert(payload: CertificationCreate, current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    profile = _get_profile(current_user, db)
    cert = StudentCertification(student_id=profile.id, **payload.model_dump())
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert


@router.put("/student/certifications/{cert_id}", response_model=CertificationResponse)
def update_cert(cert_id: int, payload: CertificationUpdate, current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    profile = _get_profile(current_user, db)
    cert = db.query(StudentCertification).filter(StudentCertification.id == cert_id, StudentCertification.student_id == profile.id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found.")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(cert, k, v)
    db.commit()
    db.refresh(cert)
    return cert


@router.delete("/student/certifications/{cert_id}", status_code=204)
def delete_cert(cert_id: int, current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    profile = _get_profile(current_user, db)
    cert = db.query(StudentCertification).filter(StudentCertification.id == cert_id, StudentCertification.student_id == profile.id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found.")
    db.delete(cert)
    db.commit()


# =================== PROJECTS ===================
@router.get("/student/projects", response_model=List[ProjectResponse])
def get_projects(current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    profile = _get_profile(current_user, db)
    return db.query(StudentProject).filter(StudentProject.student_id == profile.id).all()


@router.post("/student/projects", response_model=ProjectResponse, status_code=201)
def add_project(payload: ProjectCreate, current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    profile = _get_profile(current_user, db)
    proj = StudentProject(student_id=profile.id, **payload.model_dump())
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return proj


@router.put("/student/projects/{proj_id}", response_model=ProjectResponse)
def update_project(proj_id: int, payload: ProjectUpdate, current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    profile = _get_profile(current_user, db)
    proj = db.query(StudentProject).filter(StudentProject.id == proj_id, StudentProject.student_id == profile.id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found.")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(proj, k, v)
    db.commit()
    db.refresh(proj)
    return proj


@router.delete("/student/projects/{proj_id}", status_code=204)
def delete_project(proj_id: int, current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    profile = _get_profile(current_user, db)
    proj = db.query(StudentProject).filter(StudentProject.id == proj_id, StudentProject.student_id == profile.id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found.")
    db.delete(proj)
    db.commit()


# =================== SKILLS CATALOG ===================
@router.get("/skills", response_model=List[SkillResponse])
def get_skills_catalog(db: Session = Depends(get_db)):
    return db.query(Skill).order_by(Skill.category, Skill.name).all()
