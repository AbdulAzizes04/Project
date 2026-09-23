from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.student import StudentProfile, AcademicRecord, AptitudeScore, CareerInterest
from app.schemas.student import (
    StudentProfileCreate, StudentProfileResponse,
    AcademicRecordCreate, AcademicRecordResponse,
    AptitudeScoreCreate, AptitudeScoreResponse,
    CareerInterestCreate, CareerInterestResponse,
    FullStudentProfileResponse, ProfileCompletionSection
)
from app.middleware.auth_middleware import require_student

router = APIRouter(prefix="/student", tags=["Student Profile"])


def _calc_completion(profile, academic, aptitude, interests, skills_count, certs_count, projects_count):
    sections = [
        ProfileCompletionSection(section="Personal Info", completed=bool(profile and profile.name and profile.phone and profile.batch), score=15),
        ProfileCompletionSection(section="Academic Records", completed=bool(academic and academic.cgpa), score=20),
        ProfileCompletionSection(section="Technical Skills", completed=skills_count >= 3, score=20),
        ProfileCompletionSection(section="Projects", completed=projects_count >= 1, score=15),
        ProfileCompletionSection(section="Certifications", completed=certs_count >= 1, score=10),
        ProfileCompletionSection(section="Aptitude Scores", completed=bool(aptitude and aptitude.total_score > 0), score=10),
        ProfileCompletionSection(section="Career Interests", completed=bool(interests and interests.career_interests), score=10),
    ]
    completed_score = sum(s.score for s in sections if s.completed)
    return sections, float(completed_score)


@router.get("/profile", response_model=FullStudentProfileResponse)
def get_full_profile(current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    from app.models.skill import StudentSkill
    from app.models.portfolio import StudentCertification, StudentProject

    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    student_id = profile.id if profile else None

    academic = db.query(AcademicRecord).filter(AcademicRecord.student_id == student_id).first() if student_id else None
    aptitude = db.query(AptitudeScore).filter(AptitudeScore.student_id == student_id).first() if student_id else None
    interests = db.query(CareerInterest).filter(CareerInterest.student_id == student_id).first() if student_id else None
    skills_count = db.query(StudentSkill).filter(StudentSkill.student_id == student_id).count() if student_id else 0
    certs_count = db.query(StudentCertification).filter(StudentCertification.student_id == student_id).count() if student_id else 0
    projects_count = db.query(StudentProject).filter(StudentProject.student_id == student_id).count() if student_id else 0

    sections, pct = _calc_completion(profile, academic, aptitude, interests, skills_count, certs_count, projects_count)

    return FullStudentProfileResponse(
        profile=profile,
        academic=academic,
        aptitude=aptitude,
        interests=interests,
        skills_count=skills_count,
        certifications_count=certs_count,
        projects_count=projects_count,
        completion_percentage=pct,
        completion_sections=sections
    )


@router.put("/profile", response_model=StudentProfileResponse)
def update_profile(payload: StudentProfileCreate, current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        profile = StudentProfile(user_id=current_user.id, **payload.model_dump())
        db.add(profile)
    else:
        for k, v in payload.model_dump(exclude_unset=True).items():
            setattr(profile, k, v)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/academic", response_model=AcademicRecordResponse)
def get_academic(current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found.")
    record = db.query(AcademicRecord).filter(AcademicRecord.student_id == profile.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Academic record not found.")
    return record


@router.put("/academic", response_model=AcademicRecordResponse)
def update_academic(payload: AcademicRecordCreate, current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found.")
    record = db.query(AcademicRecord).filter(AcademicRecord.student_id == profile.id).first()
    if not record:
        record = AcademicRecord(student_id=profile.id, **payload.model_dump())
        db.add(record)
    else:
        for k, v in payload.model_dump(exclude_unset=True).items():
            setattr(record, k, v)
    db.commit()
    db.refresh(record)
    return record


@router.get("/aptitude", response_model=AptitudeScoreResponse)
def get_aptitude(current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found.")
    aptitude = db.query(AptitudeScore).filter(AptitudeScore.student_id == profile.id).first()
    if not aptitude:
        raise HTTPException(status_code=404, detail="Aptitude scores not found.")
    return aptitude


@router.put("/aptitude", response_model=AptitudeScoreResponse)
def update_aptitude(payload: AptitudeScoreCreate, current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found.")
    aptitude = db.query(AptitudeScore).filter(AptitudeScore.student_id == profile.id).first()
    data = payload.model_dump(exclude_unset=True)
    total = (
        (payload.quantitative_score or 0) +
        (payload.logical_reasoning_score or 0) +
        (payload.verbal_score or 0) +
        (payload.technical_aptitude_score or 0)
    ) / 4.0
    data["total_score"] = round(total, 2)
    if not aptitude:
        aptitude = AptitudeScore(student_id=profile.id, **data)
        db.add(aptitude)
    else:
        for k, v in data.items():
            setattr(aptitude, k, v)
    db.commit()
    db.refresh(aptitude)
    return aptitude


@router.get("/interests", response_model=CareerInterestResponse)
def get_interests(current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found.")
    interests = db.query(CareerInterest).filter(CareerInterest.student_id == profile.id).first()
    if not interests:
        raise HTTPException(status_code=404, detail="Career interests not found.")
    return interests


@router.put("/interests", response_model=CareerInterestResponse)
def update_interests(payload: CareerInterestCreate, current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found.")
    interests = db.query(CareerInterest).filter(CareerInterest.student_id == profile.id).first()
    if not interests:
        interests = CareerInterest(student_id=profile.id, **payload.model_dump())
        db.add(interests)
    else:
        for k, v in payload.model_dump(exclude_unset=True).items():
            setattr(interests, k, v)
    db.commit()
    db.refresh(interests)
    return interests
