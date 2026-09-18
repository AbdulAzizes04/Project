import uuid
import cv2
import base64
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.session import get_db
from app.models import EvidenceItem, Investigation
from app.schemas import EvidenceItemCreate, EvidenceItemResponse
from app.ai.enhancement import LowLightEnhancer

router = APIRouter(prefix="/api/evidence", tags=["Forensic Evidence & Enhancement"])

enhancer = LowLightEnhancer()

@router.get("/investigation/{investigation_id}", response_model=List[EvidenceItemResponse])
def get_evidence_items(investigation_id: str, db: Session = Depends(get_db)):
    return db.query(EvidenceItem).filter(EvidenceItem.investigation_id == investigation_id).order_by(EvidenceItem.created_at.desc()).all()

@router.post("/marker/{investigation_id}", response_model=EvidenceItemResponse)
def add_evidence_marker(investigation_id: str, payload: EvidenceItemCreate, db: Session = Depends(get_db)):
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    ev = EvidenceItem(
        id=str(uuid.uuid4()),
        investigation_id=investigation_id,
        title=payload.title,
        category=payload.category,
        timestamp=payload.timestamp or "07:45:00 PM",
        camera_id=payload.camera_id or "Camera 01",
        frame_url="https://images.unsplash.com/photo-1508847154043-be5407fcaa5a?w=600&auto=format&fit=crop&q=60",
        notes=payload.notes or "Investigator flagged critical forensic marker"
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev

@router.get("/low-light-demo")
def get_low_light_demo_frame():
    """Returns sample low-light enhancement comparison values and presets."""
    return {
        "presets": [
            {"name": "Deep Shadow (Night Vault)", "gamma": 1.75, "clip_limit": 3.5, "denoise": True},
            {"name": "Perimeter Parking (Sodium Vapor)", "gamma": 1.45, "clip_limit": 2.5, "denoise": True},
            {"name": "Glared Corridor (Headlight Compensation)", "gamma": 1.2, "clip_limit": 2.0, "denoise": False}
        ],
        "original_sample_url": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=600&auto=format&fit=crop&q=60",
        "enhanced_sample_url": "https://images.unsplash.com/photo-1517457373958-b7bdd4587205?w=600&auto=format&fit=crop&q=60",
        "algorithm": "LAB CLAHE + Non-linear Gamma Equalization + Bilateral Edge Denoising"
    }
