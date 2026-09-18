"""
Reports Router — PDF generation and download
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path

from database.db import get_db, Prediction
from routers.predictions import _serialize
from services.pdf_service import generate_report

router = APIRouter()
REPORTS_DIR = Path(__file__).resolve().parent.parent.parent / "reports"


@router.post("/generate/{pred_id}")
async def generate_prediction_report(pred_id: int, db: Session = Depends(get_db)):
    pred = db.query(Prediction).filter(Prediction.id == pred_id).first()
    if not pred:
        raise HTTPException(404, "Prediction not found")
    data = _serialize(pred)
    filename = generate_report(data)
    pred.report_path = filename
    db.commit()
    return {"filename": filename, "url": f"/reports/{filename}"}


@router.get("/download/{filename}")
async def download_report(filename: str):
    path = REPORTS_DIR / filename
    if not path.exists():
        raise HTTPException(404, "Report not found")
    return FileResponse(
        str(path),
        media_type="application/pdf",
        filename=filename
    )


@router.get("/list")
async def list_reports(db: Session = Depends(get_db)):
    preds = db.query(Prediction).filter(Prediction.report_path.isnot(None)).all()
    return [{"id": p.id, "patient_name": p.patient_name, "patient_id": p.patient_id,
             "filename": p.report_path, "created_at": p.created_at.isoformat()} for p in preds]
