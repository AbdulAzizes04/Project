"""
API Endpoints for Medical Image Upload & Ingestion.
"""

from pathlib import Path
import time
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from backend.config import DATASETS_DIR, SUPPORTED_EXTENSIONS
from backend.preprocessing.image_processor import validate_image_file, preprocess_image, InvalidImageError
from backend.database import save_image_record
from backend.utils.helpers import setup_logger

logger = setup_logger("API_Upload")
router = APIRouter(prefix="/api", tags=["Upload"])

UPLOAD_DIR = DATASETS_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class UploadResponse(BaseModel):
    image_id: int
    filename: str
    original_size_bytes: int
    dimensions: list
    channels: int
    preview_url: str
    status: str

@router.post("/upload", response_model=UploadResponse)
async def upload_medical_image(file: UploadFile = File(...)):
    """
    Validates, stores, and registers an uploaded medical image.
    Grayscale MRI, CT, and X-ray formats supported (.png, .jpg, .bmp, .tif).
    """
    ext = Path(file.filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file extension '{ext}'. Supported: {sorted(list(SUPPORTED_EXTENSIONS))}"
        )

    # Save to disk
    unique_filename = f"upload_{int(time.time() * 1000)}_{file.filename}"
    save_path = UPLOAD_DIR / unique_filename

    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Validate with image processor
        val_info = validate_image_file(save_path)
        dims = list(val_info["dimensions"])  # [width, height]
        size_bytes = val_info["size_bytes"]
        channels = val_info["channels"]

        # Insert record in SQLite
        img_id = save_image_record(
            filename=unique_filename,
            original_path=str(save_path),
            size_bytes=size_bytes,
            width=dims[0],
            height=dims[1],
            channels=channels
        )

        logger.info(f"Image uploaded successfully: ID={img_id}, Name={unique_filename}, Size={size_bytes}B")

        return UploadResponse(
            image_id=img_id,
            filename=unique_filename,
            original_size_bytes=size_bytes,
            dimensions=dims,
            channels=channels,
            preview_url=f"/media/uploads/{unique_filename}",
            status="SUCCESS"
        )
    except InvalidImageError as e:
        if save_path.exists():
            save_path.unlink()
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        if save_path.exists():
            save_path.unlink()
        logger.error(f"Error handling upload: {e}")
        raise HTTPException(status_code=500, detail=f"Internal upload error: {str(e)}")
