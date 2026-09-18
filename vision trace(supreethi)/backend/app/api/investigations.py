import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.database.session import get_db
from app.models import (
    Investigation, IncidentDetails, Video, ReferenceImage,
    DetectedPerson, EvidenceItem, TimelineEvent, Report, ProcessingJob
)
from app.schemas import (
    InvestigationCreate, InvestigationResponse, DashboardStats
)

router = APIRouter(prefix="/api/investigations", tags=["Investigations"])

@router.get("/dashboard-stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_invs = db.query(Investigation).count()
    active_invs = db.query(Investigation).filter(Investigation.status.in_(["Processing", "Pending"])).count()
    total_videos = db.query(Video).count()
    total_persons = db.query(DetectedPerson).count()
    total_evidence = db.query(EvidenceItem).count()
    total_reports = db.query(Report).count()

    recent = db.query(Investigation).order_by(Investigation.created_at.desc()).limit(10).all()
    recent_list = []
    for inv in recent:
        inc = inv.incident
        recent_list.append({
            "id": inv.id,
            "case_id": inv.case_id,
            "title": inv.title,
            "incident_type": inc.incident_type if inc else "Theft",
            "location": inc.location if inc else "Downtown Sector",
            "date": inc.incident_date if inc else "2026-09-08",
            "status": inv.status,
            "priority": inv.priority,
            "videos_count": len(inv.videos),
            "persons_count": len(inv.detected_persons)
        })

    return {
        "active_investigations": max(active_invs, 1 if total_invs > 0 else 0),
        "total_videos_processed": total_videos,
        "persons_detected": total_persons,
        "evidence_items": total_evidence,
        "reports_generated": total_reports,
        "recent_investigations": recent_list
    }

@router.get("", response_model=List[InvestigationResponse])
def list_investigations(db: Session = Depends(get_db)):
    return db.query(Investigation).order_by(Investigation.created_at.desc()).all()

@router.post("", response_model=InvestigationResponse)
def create_investigation(payload: InvestigationCreate, db: Session = Depends(get_db)):
    # Check if case_id exists
    existing = db.query(Investigation).filter(Investigation.case_id == payload.case_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Investigation with Case ID '{payload.case_id}' already exists.")

    inv_id = str(uuid.uuid4())
    inv = Investigation(
        id=inv_id,
        case_id=payload.case_id,
        title=payload.title,
        status="Pending",
        priority=payload.priority
    )
    db.add(inv)
    db.flush()

    inc = IncidentDetails(
        id=str(uuid.uuid4()),
        investigation_id=inv_id,
        incident_type=payload.incident.incident_type,
        incident_date=payload.incident.incident_date,
        incident_time=payload.incident.incident_time,
        location=payload.incident.location,
        police_station=payload.incident.police_station,
        investigator_name=payload.incident.investigator_name,
        case_description=payload.incident.case_description
    )
    db.add(inc)
    db.commit()
    db.refresh(inv)
    return inv

@router.get("/{id}", response_model=InvestigationResponse)
def get_investigation(id: str, db: Session = Depends(get_db)):
    inv = db.query(Investigation).filter((Investigation.id == id) | (Investigation.case_id == id)).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return inv

@router.post("/seed-demo")
def seed_demo_case(db: Session = Depends(get_db)):
    """Seeds rich forensic surveillance demo cases for viva & showcase."""
    case_id = "CASE-2026-089"
    existing = db.query(Investigation).filter(Investigation.case_id == case_id).first()
    if existing:
        return {"message": "Demo case already seeded", "investigation_id": existing.id}

    from app.services.pipeline import ForensicAnalysisPipeline
    inv_id = str(uuid.uuid4())
    inv = Investigation(
        id=inv_id,
        case_id=case_id,
        title="Armed Jewelry Vault Heist & Perimeter Breach",
        status="Completed",
        priority="Critical"
    )
    db.add(inv)
    db.flush()

    inc = IncidentDetails(
        id=str(uuid.uuid4()),
        investigation_id=inv_id,
        incident_type="Robbery",
        incident_date="2026-09-08",
        incident_time="07:30 PM",
        location="Grand Metropolitan Exchange, Vault Sector 4",
        police_station="Central Metropolitan Police Precinct",
        investigator_name="Detective Inspector R. Harrison",
        case_description="Suspect breached perimeter at 19:30 hours wearing dark hooded tactical apparel and facial concealment. Subverted primary biometric scanner. Fled via western parking sector."
    )
    db.add(inc)

    # Add 3 videos
    cams = [
        ("Camera 01 - Main Gate Entrance", "North Access Checkpoint", "cam01_gate.mp4", 185.0, "1920x1080", 24.5),
        ("Camera 02 - Vault Corridor", "Sub-level 2 Security Hallway", "cam02_vault.mp4", 142.0, "1920x1080", 18.2),
        ("Camera 03 - West Perimeter", "Exterior Loading & Parking", "cam03_perimeter.mp4", 210.0, "1920x1080", 29.1),
    ]
    for cid, loc, fn, dur, res, sz in cams:
        v = Video(
            id=str(uuid.uuid4()),
            investigation_id=inv_id,
            camera_id=cid,
            location=loc,
            filename=fn,
            filepath=f"uploads/videos/{fn}",
            duration_seconds=dur,
            resolution=res,
            fps=30.0,
            file_size_mb=sz,
            processed=True
        )
        db.add(v)

    # Add reference image
    ref = ReferenceImage(
        id=str(uuid.uuid4()),
        investigation_id=inv_id,
        image_type="Suspect",
        filename="suspect_reference_photo.jpg",
        filepath="uploads/images/suspect_reference_photo.jpg"
    )
    db.add(ref)

    # Job
    job = ProcessingJob(
        id=str(uuid.uuid4()),
        investigation_id=inv_id,
        status="COMPLETED",
        progress_percentage=100,
        current_step="Investigation analysis complete. Human verification required.",
        logs=[
            "[19:31:02] Frame extraction complete across 3 streams",
            "[19:31:05] YOLOv8 person detection identified 14 candidates",
            "[19:31:08] Mask detector triggered: Candidate #07 face obscured by balaclava",
            "[19:31:10] Alternative Identification Pipeline Activated (Gait & Appearance)",
            "[19:31:14] MediaPipe joint kinematics isolated unique GAIT-007 profile",
            "[19:31:18] Cross-camera association verified path: Cam01 -> Cam02 -> Cam03",
            "[19:31:22] Forensic evidence timeline and PDF report compiled"
        ]
    )
    db.add(job)
    db.commit()

    pipeline = ForensicAnalysisPipeline(db)
    pipeline._process_simulated_forensics(inv, inv.videos, [ref], lambda s, p: None)
    pipeline._ensure_timeline_events(inv)

    return {"message": "Demo case seeded successfully", "investigation_id": inv_id}
