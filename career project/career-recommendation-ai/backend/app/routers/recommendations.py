"""
FastAPI Recommendation Router - integrates the ML engine into the API.
Handles recommendation generation, SHAP/LIME retrieval, skill gap, and careers.
"""

import os
import sys
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Ensure ml/ directory is importable
from app.utils import ml_path  # noqa: F401

from app.database import get_db
from app.models.user import User
from app.models.student import StudentProfile, AcademicRecord, AptitudeScore, CareerInterest
from app.models.skill import StudentSkill, Skill
from app.models.portfolio import StudentCertification, StudentProject
from app.models.career import CareerRole, CareerSkill
from app.models.recommendation import CareerRecommendation, RecommendationExplanation, SkillGap
from app.models.learning import LearningResource, StudentProgress
from app.schemas.recommendation import (
    CareerRoleResponse, CareerRecommendationResponse,
    RecommendationExplanationResponse, GenerateRecommendationRequest,
    CompareCareerRequest, SkillGapResponse, SkillGapItemResponse,
    ProgressCreate, ProgressUpdate, ProgressResponse
)
from app.middleware.auth_middleware import require_student, get_current_user

logger = logging.getLogger("career_ai.recommendation_router")
router = APIRouter(tags=["Recommendations & Careers"])


def _get_student(user: User, db: Session) -> StudentProfile:
    p = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Student profile not found. Complete your profile first.")
    return p


def _build_student_data(student: StudentProfile, db: Session) -> dict:
    """Assemble all student data needed by recommendation engine."""
    academic = db.query(AcademicRecord).filter(AcademicRecord.student_id == student.id).first()
    aptitude = db.query(AptitudeScore).filter(AptitudeScore.student_id == student.id).first()
    interests = db.query(CareerInterest).filter(CareerInterest.student_id == student.id).first()

    student_skills_raw = db.query(StudentSkill).filter(StudentSkill.student_id == student.id).all()
    skills = [{"skill_id": ss.skill_id, "skill_name": ss.skill.name, "proficiency_level": ss.proficiency_level} for ss in student_skills_raw]

    certs_raw = db.query(StudentCertification).filter(StudentCertification.student_id == student.id).all()
    certs = [{"certification_name": c.certification_name, "domain": c.domain} for c in certs_raw]

    projects_raw = db.query(StudentProject).filter(StudentProject.student_id == student.id).all()
    projects = [{"project_name": p.project_name, "domain": p.domain, "complexity": p.complexity, "technologies": p.technologies} for p in projects_raw]

    return {
        "academic": {
            "cgpa": academic.cgpa if academic else None,
            "tenth_percentage": academic.tenth_percentage if academic else None,
            "twelfth_percentage": academic.twelfth_percentage if academic else None,
        } if academic else {},
        "aptitude": {
            "quantitative_score": aptitude.quantitative_score if aptitude else 0,
            "logical_reasoning_score": aptitude.logical_reasoning_score if aptitude else 0,
            "verbal_score": aptitude.verbal_score if aptitude else 0,
            "technical_aptitude_score": aptitude.technical_aptitude_score if aptitude else 0,
            "total_score": aptitude.total_score if aptitude else 0,
        } if aptitude else {},
        "interests": {
            "preferred_domains": interests.preferred_domains if interests else [],
            "career_interests": interests.career_interests if interests else [],
            "preferred_technologies": interests.preferred_technologies if interests else [],
        } if interests else {},
        "skills": skills,
        "certifications": certs,
        "projects": projects,
    }


def _build_careers_for_engine(db: Session) -> List[dict]:
    """Build career data dict compatible with recommendation engine."""
    careers = db.query(CareerRole).filter(CareerRole.is_active == True).all()
    result = []
    for career in careers:
        required_skills = [
            {
                "skill_id": cs.skill_id,
                "skill_name": cs.skill.name,
                "skill_category": cs.skill.category,
                "importance_weight": cs.importance_weight,
                "is_required": cs.is_required,
                "min_proficiency": cs.min_proficiency
            }
            for cs in career.career_skills
        ]
        result.append({
            "id": career.id, "name": career.name, "slug": career.slug,
            "description": career.description, "min_cgpa": career.min_cgpa,
            "min_aptitude_score": career.min_aptitude_score,
            "required_skills": required_skills,
            "relevant_domains": []
        })
    return result


# =================== CAREERS ===================
@router.get("/careers", response_model=List[CareerRoleResponse])
def get_all_careers(db: Session = Depends(get_db)):
    return db.query(CareerRole).filter(CareerRole.is_active == True).all()


@router.get("/careers/{career_id}", response_model=CareerRoleResponse)
def get_career(career_id: int, db: Session = Depends(get_db)):
    career = db.query(CareerRole).filter(CareerRole.id == career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career role not found.")
    return career


# =================== RECOMMENDATIONS ===================
@router.post("/recommendations/generate")
def generate_recommendations(
    payload: GenerateRecommendationRequest,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    student = _get_student(current_user, db)

    # Clear old recommendations if regenerating
    if payload.regenerate:
        db.query(SkillGap).filter(SkillGap.student_id == student.id).delete()
        old_recs = db.query(CareerRecommendation).filter(CareerRecommendation.student_id == student.id).all()
        for r in old_recs:
            if r.explanation:
                db.delete(r.explanation)
            db.delete(r)
        db.commit()

    # Check if fresh recommendations already exist
    existing = db.query(CareerRecommendation).filter(CareerRecommendation.student_id == student.id).count()
    if existing > 0 and not payload.regenerate:
        return {"success": True, "message": "Recommendations already generated.", "count": existing}

    # Build data and run engine
    student_data = _build_student_data(student, db)
    careers = _build_careers_for_engine(db)

    # Import ML engine
    from ml.recommendation.engine import generate_recommendations as ml_recommend
    from ml.skill_gap.gap_analyzer import analyze_skill_gap

    try:
        recs = ml_recommend(student_data, careers)
    except Exception as exc:
        logger.error(f"Recommendation engine error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Recommendation engine failed: {str(exc)}")

    saved_ids = []
    for rec in recs:
        career_id = rec["career_id"]

        rec_obj = CareerRecommendation(
            student_id=student.id,
            career_id=career_id,
            compatibility_score=rec["compatibility_score"],
            rank_order=rec["rank_order"],
            ml_confidence=rec.get("ml_confidence", 0),
            skill_compatibility=rec.get("skill_compatibility", 0),
            academic_compatibility=rec.get("academic_compatibility", 0),
            project_compatibility=rec.get("project_compatibility", 0),
            certification_compatibility=rec.get("certification_compatibility", 0),
            aptitude_compatibility=rec.get("aptitude_compatibility", 0),
            interest_compatibility=rec.get("interest_compatibility", 0),
            domain_compatibility=rec.get("domain_compatibility", 0),
            matching_skills=rec.get("matching_skills", []),
            missing_skills=rec.get("missing_skills", [])
        )
        db.add(rec_obj)
        db.flush()

        # Save explanation
        exp_data = rec.get("explanation", {})
        exp_obj = RecommendationExplanation(
            recommendation_id=rec_obj.id,
            shap_values=exp_data.get("shap_values"),
            lime_values=exp_data.get("lime_values"),
            top_positive_factors=exp_data.get("top_positive_factors"),
            top_negative_factors=exp_data.get("top_negative_factors"),
            human_readable_text=exp_data.get("human_readable_text", "Recommendation generated.")
        )
        db.add(exp_obj)

        # Save skill gaps for this career
        career_obj = next((c for c in careers if c["id"] == career_id), None)
        if career_obj:
            gap_result = analyze_skill_gap(student_data["skills"], career_obj["required_skills"])
            for g in gap_result["strong_skills"] + gap_result["moderate_skills"] + gap_result["missing_skills"]:
                try:
                    sg = SkillGap(
                        student_id=student.id,
                        career_id=career_id,
                        skill_id=g["skill_id"],
                        gap_status=g["gap_status"],
                        student_level=g.get("student_level", "NONE"),
                        required_level=g.get("required_level", "INTERMEDIATE"),
                        learning_priority=g["learning_priority"],
                        priority_score=g.get("priority_score", 0.0)
                    )
                    db.add(sg)
                    db.flush()
                except Exception:
                    db.rollback()
                    pass

        saved_ids.append(rec_obj.id)

    db.commit()
    return {"success": True, "message": f"Generated {len(recs)} career recommendations.", "recommendation_ids": saved_ids}


@router.get("/recommendations")
def get_recommendations(current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    student = _get_student(current_user, db)
    recs = db.query(CareerRecommendation).filter(CareerRecommendation.student_id == student.id).order_by(CareerRecommendation.rank_order).all()
    result = []
    for rec in recs:
        result.append({
            "id": rec.id,
            "career_id": rec.career_id,
            "career_name": rec.career.name,
            "career_slug": rec.career.slug,
            "career_description": rec.career.description,
            "compatibility_score": rec.compatibility_score,
            "rank_order": rec.rank_order,
            "ml_confidence": rec.ml_confidence,
            "skill_compatibility": rec.skill_compatibility,
            "academic_compatibility": rec.academic_compatibility,
            "project_compatibility": rec.project_compatibility,
            "certification_compatibility": rec.certification_compatibility,
            "aptitude_compatibility": rec.aptitude_compatibility,
            "interest_compatibility": rec.interest_compatibility,
            "domain_compatibility": rec.domain_compatibility,
            "matching_skills": rec.matching_skills or [],
            "missing_skills": rec.missing_skills or [],
            "generated_at": rec.generated_at.isoformat()
        })
    return {"success": True, "data": result}


@router.get("/recommendations/{rec_id}")
def get_recommendation_detail(rec_id: int, current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    student = _get_student(current_user, db)
    rec = db.query(CareerRecommendation).filter(CareerRecommendation.id == rec_id, CareerRecommendation.student_id == student.id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found.")
    return {
        "id": rec.id,
        "career_name": rec.career.name,
        "career_description": rec.career.description,
        "compatibility_score": rec.compatibility_score,
        "rank_order": rec.rank_order,
        "skill_compatibility": rec.skill_compatibility,
        "academic_compatibility": rec.academic_compatibility,
        "project_compatibility": rec.project_compatibility,
        "matching_skills": rec.matching_skills or [],
        "missing_skills": rec.missing_skills or [],
        "explanation": {
            "human_readable_text": rec.explanation.human_readable_text if rec.explanation else "",
            "top_positive_factors": rec.explanation.top_positive_factors if rec.explanation else [],
            "top_negative_factors": rec.explanation.top_negative_factors if rec.explanation else [],
            "shap_values": rec.explanation.shap_values if rec.explanation else [],
            "lime_values": rec.explanation.lime_values if rec.explanation else [],
        } if rec.explanation else None
    }


@router.get("/recommendations/{rec_id}/shap")
def get_shap_explanation(rec_id: int, current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    student = _get_student(current_user, db)
    rec = db.query(CareerRecommendation).filter(CareerRecommendation.id == rec_id, CareerRecommendation.student_id == student.id).first()
    if not rec or not rec.explanation:
        raise HTTPException(status_code=404, detail="Explanation not found.")
    return {
        "career_name": rec.career.name,
        "compatibility_score": rec.compatibility_score,
        "shap_values": rec.explanation.shap_values,
        "top_positive_factors": rec.explanation.top_positive_factors,
        "top_negative_factors": rec.explanation.top_negative_factors,
        "human_readable_text": rec.explanation.human_readable_text
    }


@router.get("/recommendations/{rec_id}/lime")
def get_lime_explanation(rec_id: int, current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    student = _get_student(current_user, db)
    rec = db.query(CareerRecommendation).filter(CareerRecommendation.id == rec_id, CareerRecommendation.student_id == student.id).first()
    if not rec or not rec.explanation:
        raise HTTPException(status_code=404, detail="Explanation not found.")
    return {
        "career_name": rec.career.name,
        "lime_values": rec.explanation.lime_values,
        "human_readable_text": rec.explanation.human_readable_text
    }


# =================== SKILL GAP ===================
@router.get("/skill-gap/{career_id}")
def get_skill_gap(career_id: int, current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    student = _get_student(current_user, db)
    career = db.query(CareerRole).filter(CareerRole.id == career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found.")

    gaps = db.query(SkillGap).filter(SkillGap.student_id == student.id, SkillGap.career_id == career_id).all()

    def _to_item(g):
        return SkillGapItemResponse(
            skill_id=g.skill_id, skill_name=g.skill.name, skill_category=g.skill.category,
            gap_status=g.gap_status, student_level=g.student_level, required_level=g.required_level,
            learning_priority=g.learning_priority, priority_score=g.priority_score
        )

    strong = [_to_item(g) for g in gaps if g.gap_status == "STRONG"]
    moderate = [_to_item(g) for g in gaps if g.gap_status == "MODERATE"]
    missing = [_to_item(g) for g in gaps if g.gap_status == "MISSING"]
    total_req = len([g for g in gaps if g.skill.career_skills])
    matched = len(strong)

    return SkillGapResponse(
        career_id=career_id, career_name=career.name,
        strong_skills=strong, moderate_skills=moderate, missing_skills=missing,
        skill_coverage_percent=round(matched / max(len(strong) + len(moderate) + len(missing), 1) * 100, 1),
        total_required=len(strong) + len(moderate) + len(missing),
        matched_required=len(strong)
    )


# =================== CAREER COMPARISON ===================
@router.post("/careers/compare")
def compare_careers(payload: CompareCareerRequest, current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    student = _get_student(current_user, db)
    result = []
    for career_id in payload.career_ids[:4]:
        career = db.query(CareerRole).filter(CareerRole.id == career_id).first()
        if not career:
            continue
        rec = db.query(CareerRecommendation).filter(
            CareerRecommendation.student_id == student.id,
            CareerRecommendation.career_id == career_id
        ).first()
        gaps = db.query(SkillGap).filter(SkillGap.student_id == student.id, SkillGap.career_id == career_id).all()
        result.append({
            "career_id": career_id,
            "career_name": career.name,
            "compatibility_score": rec.compatibility_score if rec else None,
            "skill_compatibility": rec.skill_compatibility if rec else None,
            "academic_compatibility": rec.academic_compatibility if rec else None,
            "interest_compatibility": rec.interest_compatibility if rec else None,
            "project_compatibility": rec.project_compatibility if rec else None,
            "strong_skills_count": len([g for g in gaps if g.gap_status == "STRONG"]),
            "missing_skills_count": len([g for g in gaps if g.gap_status == "MISSING"]),
            "skill_coverage_percent": round(
                len([g for g in gaps if g.gap_status == "STRONG"]) / max(len(gaps), 1) * 100, 1
            )
        })
    return {"success": True, "comparison": result}


# =================== PROGRESS TRACKING ===================
@router.get("/student/progress", response_model=List[ProgressResponse])
def get_progress(current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    student = _get_student(current_user, db)
    return db.query(StudentProgress).filter(StudentProgress.student_id == student.id).order_by(StudentProgress.week_number).all()


@router.post("/student/progress", response_model=ProgressResponse, status_code=201)
def add_progress(payload: ProgressCreate, current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    student = _get_student(current_user, db)
    prog = StudentProgress(student_id=student.id, **payload.model_dump())
    db.add(prog)
    db.commit()
    db.refresh(prog)
    return prog


@router.put("/student/progress/{prog_id}", response_model=ProgressResponse)
def update_progress(prog_id: int, payload: ProgressUpdate, current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    student = _get_student(current_user, db)
    prog = db.query(StudentProgress).filter(StudentProgress.id == prog_id, StudentProgress.student_id == student.id).first()
    if not prog:
        raise HTTPException(status_code=404, detail="Progress item not found.")
    prog.status = payload.status
    prog.progress_percent = payload.progress_percent
    if payload.notes:
        prog.notes = payload.notes
    db.commit()
    db.refresh(prog)
    return prog


@router.get("/learning-roadmap")
def get_learning_roadmap(current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    """Returns personalized learning roadmap from stored skill gap + learning resources."""
    student = _get_student(current_user, db)

    # Get top-ranked recommendation's career
    top_rec = db.query(CareerRecommendation).filter(CareerRecommendation.student_id == student.id).order_by(CareerRecommendation.rank_order).first()
    if not top_rec:
        return {"success": False, "message": "Generate recommendations first."}

    gaps = db.query(SkillGap).filter(SkillGap.student_id == student.id, SkillGap.career_id == top_rec.career_id).all()

    def gap_to_dict(g):
        return {
            "skill_id": g.skill_id, "skill_name": g.skill.name,
            "gap_status": g.gap_status, "learning_priority": g.learning_priority,
            "priority_score": g.priority_score, "student_level": g.student_level,
            "required_level": g.required_level
        }

    missing = [gap_to_dict(g) for g in gaps if g.gap_status == "MISSING"]
    moderate = [gap_to_dict(g) for g in gaps if g.gap_status == "MODERATE"]

    # Get learning resources for these skills
    skill_ids = list({g["skill_id"] for g in missing + moderate})
    resources_raw = db.query(LearningResource).filter(LearningResource.skill_id.in_(skill_ids)).all()
    resources = [{"skill_id": r.skill_id, "title": r.title, "url": r.url, "estimated_hours": r.estimated_hours} for r in resources_raw]

    from ml.skill_gap.gap_analyzer import generate_learning_roadmap
    roadmap = generate_learning_roadmap(missing, moderate, resources)

    return {"success": True, "career_name": top_rec.career.name, "roadmap": roadmap}
