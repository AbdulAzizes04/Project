"""
Appointments Router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database.db import get_db, Appointment
from schemas import AppointmentCreate, AppointmentOut

router = APIRouter()


@router.post("/", response_model=AppointmentOut)
async def create_appointment(req: AppointmentCreate, db: Session = Depends(get_db)):
    apt = Appointment(**req.dict())
    db.add(apt)
    db.commit()
    db.refresh(apt)
    return apt


@router.get("/", response_model=List[AppointmentOut])
async def list_appointments(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Appointment).order_by(Appointment.appointment_date).offset(skip).limit(limit).all()


@router.get("/{apt_id}", response_model=AppointmentOut)
async def get_appointment(apt_id: int, db: Session = Depends(get_db)):
    apt = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not apt:
        raise HTTPException(404, "Appointment not found")
    return apt


@router.patch("/{apt_id}/status")
async def update_status(apt_id: int, status: str, db: Session = Depends(get_db)):
    apt = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not apt:
        raise HTTPException(404, "Appointment not found")
    apt.status = status
    db.commit()
    return {"detail": "Status updated", "status": status}


@router.delete("/{apt_id}")
async def delete_appointment(apt_id: int, db: Session = Depends(get_db)):
    apt = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not apt:
        raise HTTPException(404, "Not found")
    db.delete(apt)
    db.commit()
    return {"detail": "Deleted"}
