import os
import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.models import Report, Investigation, DetectedPerson, TimelineEvent, EvidenceItem
from app.schemas import ReportResponse
from app.services.report_generator import ForensicReportGenerator

router = APIRouter(prefix="/api/reports", tags=["Forensic Reports"])

report_gen = ForensicReportGenerator()

@router.get("/investigation/{investigation_id}", response_model=List[ReportResponse])
def get_investigation_reports(investigation_id: str, db: Session = Depends(get_db)):
    return db.query(Report).filter(Report.investigation_id == investigation_id).order_by(Report.created_at.desc()).all()

@router.get("/{id}", response_model=ReportResponse)
def get_report(id: str, db: Session = Depends(get_db)):
    rep = db.query(Report).filter(Report.id == id).first()
    if not rep:
        raise HTTPException(status_code=404, detail="Report not found")
    return rep

@router.post("/generate/{investigation_id}", response_model=ReportResponse)
def generate_report(investigation_id: str, db: Session = Depends(get_db)):
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    persons = db.query(DetectedPerson).filter(DetectedPerson.investigation_id == investigation_id).all()
    timeline = db.query(TimelineEvent).filter(TimelineEvent.investigation_id == investigation_id).order_by(TimelineEvent.timestamp).all()
    evidence = db.query(EvidenceItem).filter(EvidenceItem.investigation_id == investigation_id).all()

    pdf_path = report_gen.generate_pdf_report(inv, persons, timeline, evidence)

    rep = Report(
        id=str(uuid.uuid4()),
        investigation_id=inv.id,
        report_number=f"REP-{inv.case_id}-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M')}",
        title=f"AI-Assisted Forensic Investigation Report: {inv.title}",
        pdf_path=pdf_path,
        executive_summary=(
            f"Forensic surveillance analysis completed for incident {inv.case_id}. "
            f"Multi-camera tracking isolated {len(persons)} person tracks. "
            f"Face occlusion analysis detected {len([p for p in persons if p.face_visibility == 'Masked'])} masked subjects, "
            f"activating alternative gait and appearance signatures."
        ),
        ai_findings={
            "total_cameras": len(inv.videos),
            "persons_detected": len(persons),
            "evidence_events": len(timeline),
            "verification_status": "Human Investigator Verification Required"
        }
    )
    db.add(rep)
    db.commit()
    db.refresh(rep)
    return rep

@router.get("/{id}/download")
def download_report_pdf(id: str, db: Session = Depends(get_db)):
    rep = db.query(Report).filter(Report.id == id).first()
    if not rep or not rep.pdf_path or not os.path.exists(rep.pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found on disk")
    return FileResponse(
        rep.pdf_path,
        media_type="application/pdf",
        filename=os.path.basename(rep.pdf_path)
    )
