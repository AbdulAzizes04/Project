from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.career import CareerRole, CareerSkill
from app.models.skill import Skill, SkillAlias, StudentSkill
from app.models.student import StudentProfile
from app.models.recommendation import CareerRecommendation, SkillGap
from app.models.admin_analytics import ModelMetric
from app.schemas.recommendation import CareerRoleResponse
from app.middleware.auth_middleware import require_admin
import json
import os

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/students")
def get_all_students(current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    students = db.query(StudentProfile).all()
    result = []
    for s in students:
        result.append({
            "id": s.id, "name": s.name, "email": s.user.email,
            "batch": s.batch, "branch": s.branch,
            "skills_count": len(s.skills),
            "projects_count": len(s.projects),
            "certifications_count": len(s.certifications),
            "has_recommendations": len(s.recommendations) > 0
        })
    return {"success": True, "students": result, "total": len(result)}


@router.get("/careers")
def get_careers(current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    careers = db.query(CareerRole).all()
    result = []
    for c in careers:
        result.append({
            "id": c.id, "name": c.name, "slug": c.slug,
            "difficulty_level": c.difficulty_level, "is_active": c.is_active,
            "min_cgpa": c.min_cgpa, "salary_range": c.salary_range,
            "required_skills_count": len([cs for cs in c.career_skills if cs.is_required]),
            "preferred_skills_count": len([cs for cs in c.career_skills if not cs.is_required])
        })
    return {"success": True, "careers": result}


@router.post("/careers", status_code=201)
def create_career(payload: dict, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    career = CareerRole(**{k: v for k, v in payload.items() if hasattr(CareerRole, k)})
    db.add(career)
    db.commit()
    db.refresh(career)
    return {"success": True, "career_id": career.id, "message": "Career role created."}


@router.put("/careers/{career_id}")
def update_career(career_id: int, payload: dict, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    career = db.query(CareerRole).filter(CareerRole.id == career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found.")
    for k, v in payload.items():
        if hasattr(career, k):
            setattr(career, k, v)
    db.commit()
    return {"success": True, "message": "Career updated."}


@router.delete("/careers/{career_id}")
def delete_career(career_id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    career = db.query(CareerRole).filter(CareerRole.id == career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found.")
    career.is_active = False  # soft delete
    db.commit()
    return {"success": True, "message": "Career deactivated."}


@router.get("/skills")
def get_all_skills(current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    skills = db.query(Skill).order_by(Skill.category, Skill.name).all()
    result = [{"id": s.id, "name": s.name, "category": s.category,
               "aliases": [a.alias for a in s.aliases]} for s in skills]
    return {"success": True, "skills": result, "total": len(result)}


@router.post("/skills", status_code=201)
def create_skill(payload: dict, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    existing = db.query(Skill).filter(Skill.name == payload.get("name")).first()
    if existing:
        raise HTTPException(status_code=409, detail="Skill already exists.")
    skill = Skill(name=payload["name"], category=payload.get("category", "General"), description=payload.get("description"))
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return {"success": True, "skill_id": skill.id}


@router.get("/analytics")
def get_analytics(current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    from app.models.portfolio import StudentProject, StudentCertification

    total_students = db.query(StudentProfile).count()
    total_careers = db.query(CareerRole).filter(CareerRole.is_active == True).count()
    total_skills = db.query(Skill).count()
    total_recs = db.query(CareerRecommendation).count()

    # Most recommended careers
    from sqlalchemy import func
    career_counts = db.query(
        CareerRecommendation.career_id,
        func.count(CareerRecommendation.id).label("count")
    ).filter(CareerRecommendation.rank_order == 1).group_by(CareerRecommendation.career_id).all()
    
    popular_careers = []
    for cc in career_counts:
        career = db.query(CareerRole).filter(CareerRole.id == cc.career_id).first()
        if career:
            popular_careers.append({"career_name": career.name, "student_count": cc.count})

    # Most common skill gaps
    gap_counts = db.query(
        SkillGap.skill_id,
        func.count(SkillGap.id).label("count")
    ).filter(SkillGap.gap_status == "MISSING").group_by(SkillGap.skill_id).order_by(func.count(SkillGap.id).desc()).limit(10).all()
    
    common_gaps = []
    for gc in gap_counts:
        skill = db.query(Skill).filter(Skill.id == gc.skill_id).first()
        if skill:
            common_gaps.append({"skill_name": skill.name, "missing_count": gc.count})

    # Skill distribution
    skill_counts = db.query(
        StudentSkill.skill_id,
        func.count(StudentSkill.id).label("count")
    ).group_by(StudentSkill.skill_id).order_by(func.count(StudentSkill.id).desc()).limit(15).all()
    
    skill_dist = []
    for sc in skill_counts:
        skill = db.query(Skill).filter(Skill.id == sc.skill_id).first()
        if skill:
            skill_dist.append({"skill_name": skill.name, "student_count": sc.count})

    return {
        "success": True,
        "summary": {
            "total_students": total_students,
            "total_career_roles": total_careers,
            "total_skills": total_skills,
            "total_recommendations_generated": total_recs
        },
        "popular_careers": popular_careers,
        "most_common_skill_gaps": common_gaps,
        "skill_distribution": skill_dist
    }


@router.get("/model-performance")
def get_model_performance(current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Return saved ML model metrics from artifacts."""
    ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "artifacts")
    metrics_path = os.path.join(ARTIFACTS_DIR, "model_metrics.json")
    if not os.path.exists(metrics_path):
        return {"success": False, "message": "Model metrics not found. Run ml/training/train_model.py first."}
    with open(metrics_path) as f:
        metrics = json.load(f)
    return {"success": True, "metrics": metrics}
