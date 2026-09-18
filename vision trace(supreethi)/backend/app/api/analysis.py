import uuid
import threading
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database.session import get_db, SessionLocal
from app.models import Investigation, ProcessingJob
from app.schemas import ProcessingJobResponse
from app.services.pipeline import ForensicAnalysisPipeline

router = APIRouter(prefix="/api/analysis", tags=["AI Analysis Pipeline"])

def run_pipeline_thread(investigation_id: str, job_id: str):
    db = SessionLocal()
    try:
        pipeline = ForensicAnalysisPipeline(db)
        pipeline.run_pipeline(investigation_id, job_id)
    finally:
        db.close()

@router.post("/start/{investigation_id}", response_model=ProcessingJobResponse)
def start_analysis(investigation_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    job_id = str(uuid.uuid4())
    job = ProcessingJob(
        id=job_id,
        investigation_id=investigation_id,
        status="QUEUED",
        progress_percentage=0,
        current_step="Queued for forensic computer vision analysis...",
        logs=["[Initial] Investigation submitted to AI surveillance pipeline"]
    )
    db.add(job)
    inv.status = "Processing"
    db.commit()
    db.refresh(job)

    # Launch background thread
    threading.Thread(target=run_pipeline_thread, args=(investigation_id, job_id), daemon=True).start()

    return job

@router.get("/job/{job_id}", response_model=ProcessingJobResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Processing job not found")
    return job

@router.get("/investigation/{investigation_id}/latest-job", response_model=ProcessingJobResponse)
def get_latest_job(investigation_id: str, db: Session = Depends(get_db)):
    job = db.query(ProcessingJob).filter(ProcessingJob.investigation_id == investigation_id).order_by(ProcessingJob.created_at.desc()).first()
    if not job:
        raise HTTPException(status_code=404, detail="No processing job found for this investigation")
    return job
