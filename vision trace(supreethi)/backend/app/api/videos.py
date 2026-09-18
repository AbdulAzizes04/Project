import os
import uuid
import cv2
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.session import get_db
from app.models import Video, ReferenceImage, Investigation
from app.schemas import VideoResponse, ReferenceImageResponse

router = APIRouter(prefix="/api/videos", tags=["Videos & Reference Media"])

UPLOAD_VIDEO_DIR = "uploads/videos"
UPLOAD_IMAGE_DIR = "uploads/images"
os.makedirs(UPLOAD_VIDEO_DIR, exist_ok=True)
os.makedirs(UPLOAD_IMAGE_DIR, exist_ok=True)

@router.post("/upload", response_model=VideoResponse)
async def upload_video(
    investigation_id: str = Form(...),
    camera_id: str = Form("Camera 01"),
    location: str = Form("Primary Entrance"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    file_ext = os.path.splitext(file.filename)[1] or ".mp4"
    safe_name = f"{uuid.uuid4()}_{file.filename}"
    save_path = os.path.join(UPLOAD_VIDEO_DIR, safe_name)

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    file_size_mb = round(len(content) / (1024 * 1024), 2)

    # Read video properties using OpenCV
    duration = 120.0
    resolution = "1920x1080"
    fps = 30.0

    try:
        cap = cv2.VideoCapture(save_path)
        if cap.isOpened():
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = float(cap.get(cv2.CAP_PROP_FPS)) or 30.0
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if w > 0 and h > 0:
                resolution = f"{w}x{h}"
            if fps > 0 and total_frames > 0:
                duration = round(total_frames / fps, 1)
            cap.release()
    except Exception:
        pass

    video_obj = Video(
        id=str(uuid.uuid4()),
        investigation_id=investigation_id,
        camera_id=camera_id,
        location=location,
        filename=file.filename,
        filepath=save_path,
        duration_seconds=duration,
        resolution=resolution,
        fps=fps,
        file_size_mb=file_size_mb,
        processed=False
    )
    db.add(video_obj)
    db.commit()
    db.refresh(video_obj)
    return video_obj

@router.post("/reference-image/upload", response_model=ReferenceImageResponse)
async def upload_reference_image(
    investigation_id: str = Form(...),
    image_type: str = Form("Suspect"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    safe_name = f"{uuid.uuid4()}_{file.filename}"
    save_path = os.path.join(UPLOAD_IMAGE_DIR, safe_name)

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    ref_obj = ReferenceImage(
        id=str(uuid.uuid4()),
        investigation_id=investigation_id,
        image_type=image_type,
        filename=file.filename,
        filepath=save_path
    )
    db.add(ref_obj)
    db.commit()
    db.refresh(ref_obj)
    return ref_obj
