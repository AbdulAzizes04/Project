"""
VisionTrace AI — Reports API (PDF + DOCX)
"""
import io
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database.database import get_db
from database import models
from reports.pdf_generator import generate_pdf
from reports.docx_generator import generate_docx

router = APIRouter(prefix="/api/reports", tags=["Reports"])


def _get_case_data(case_id: int, db: Session) -> dict:
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(404, "Case not found")
    tracks = db.query(models.Track).filter(models.Track.case_id == case_id).all()
    evidence = (
        db.query(models.Evidence)
        .filter(models.Evidence.case_id == case_id)
        .order_by(models.Evidence.timestamp)
        .all()
    )
    analysis = (
        db.query(models.AnalysisResult)
        .filter(models.AnalysisResult.case_id == case_id)
        .all()
    )
    return {"case": case, "tracks": tracks, "evidence": evidence, "analysis": analysis}


@router.get("/{case_id}/pdf")
def download_pdf(case_id: int, db: Session = Depends(get_db)):
    data = _get_case_data(case_id, db)
    pdf_bytes = generate_pdf(data)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=visiontrace_case_{case_id}.pdf"},
    )


@router.get("/{case_id}/docx")
def download_docx(case_id: int, db: Session = Depends(get_db)):
    data = _get_case_data(case_id, db)
    docx_bytes = generate_docx(data)
    return StreamingResponse(
        io.BytesIO(docx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=visiontrace_case_{case_id}.docx"},
    )
