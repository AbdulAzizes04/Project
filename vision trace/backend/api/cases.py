"""
VisionTrace AI — Cases API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database.database import get_db
from database import models, schemas

router = APIRouter(prefix="/api/cases", tags=["Cases"])


@router.post("/create", response_model=schemas.CaseOut)
def create_case(data: schemas.CaseCreate, db: Session = Depends(get_db)):
    case = models.Case(case_name=data.case_name, notes=data.notes)
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


@router.get("", response_model=List[schemas.CaseOut])
def list_cases(db: Session = Depends(get_db)):
    return db.query(models.Case).order_by(models.Case.id.desc()).all()


@router.get("/{case_id}", response_model=schemas.CaseOut)
def get_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(404, "Case not found")
    return case


@router.delete("/{case_id}")
def delete_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(404, "Case not found")
    db.delete(case)
    db.commit()
    return {"message": "Case deleted"}


@router.get("/{case_id}/tracks", response_model=List[schemas.TrackOut])
def get_tracks(case_id: int, db: Session = Depends(get_db)):
    return db.query(models.Track).filter(models.Track.case_id == case_id).all()


@router.get("/{case_id}/timeline", response_model=List[schemas.EvidenceOut])
def get_timeline(case_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Evidence)
        .filter(models.Evidence.case_id == case_id)
        .order_by(models.Evidence.timestamp)
        .all()
    )


@router.get("/{case_id}/analysis", response_model=List[schemas.AnalysisResultOut])
def get_analysis(case_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.AnalysisResult)
        .filter(models.AnalysisResult.case_id == case_id)
        .all()
    )
