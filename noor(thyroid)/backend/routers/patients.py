"""
Patients Router — CRUD
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from database.db import get_db, Patient
from schemas import PatientCreate, PatientOut
from routers.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=PatientOut)
async def create_patient(req: PatientCreate, db: Session = Depends(get_db)):
    patient_id = f"PAT-{str(uuid.uuid4())[:8].upper()}"
    # Auto-compute BMI
    bmi = req.bmi
    if not bmi and req.weight and req.height:
        bmi = round(req.weight / ((req.height / 100) ** 2), 2)
    patient = Patient(**req.dict(), patient_id=patient_id, bmi=bmi)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("/", response_model=List[PatientOut])
async def list_patients(
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    q = db.query(Patient)
    if search:
        q = q.filter(Patient.name.ilike(f"%{search}%") | Patient.patient_id.ilike(f"%{search}%"))
    return q.order_by(Patient.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/count")
async def count_patients(db: Session = Depends(get_db)):
    return {"count": db.query(Patient).count()}


@router.get("/{patient_id}", response_model=PatientOut)
async def get_patient(patient_id: str, db: Session = Depends(get_db)):
    p = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not p:
        raise HTTPException(404, "Patient not found")
    return p


@router.put("/{patient_id}", response_model=PatientOut)
async def update_patient(patient_id: str, req: PatientCreate, db: Session = Depends(get_db)):
    p = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not p:
        raise HTTPException(404, "Patient not found")
    for k, v in req.dict(exclude_unset=True).items():
        setattr(p, k, v)
    p.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{patient_id}")
async def delete_patient(patient_id: str, db: Session = Depends(get_db)):
    p = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not p:
        raise HTTPException(404, "Patient not found")
    db.delete(p)
    db.commit()
    return {"detail": "Patient deleted"}
