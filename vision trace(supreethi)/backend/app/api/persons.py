from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.models import DetectedPerson, GaitAnalysis
from app.schemas import DetectedPersonResponse, GaitAnalysisResponse

router = APIRouter(prefix="/api/persons", tags=["Persons of Interest"])

@router.get("/investigation/{investigation_id}", response_model=List[DetectedPersonResponse])
def get_investigation_persons(investigation_id: str, db: Session = Depends(get_db)):
    persons = db.query(DetectedPerson).filter(DetectedPerson.investigation_id == investigation_id).order_by(DetectedPerson.ai_relevance_score.desc()).all()
    return persons

@router.get("/{id}", response_model=DetectedPersonResponse)
def get_person_detail(id: str, db: Session = Depends(get_db)):
    person = db.query(DetectedPerson).filter(DetectedPerson.id == id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person

@router.get("/{id}/gait", response_model=GaitAnalysisResponse)
def get_person_gait(id: str, db: Session = Depends(get_db)):
    gait = db.query(GaitAnalysis).filter(GaitAnalysis.detected_person_id == id).first()
    if not gait:
        raise HTTPException(status_code=404, detail="Gait profile not found for this person")
    return gait
