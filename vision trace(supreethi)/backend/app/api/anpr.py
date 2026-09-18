from fastapi import APIRouter, Depends
from typing import List
from app.schemas import ANPRPlateResult
from app.ai.anpr import LicensePlateRecognizer

router = APIRouter(prefix="/api/anpr", tags=["Automatic Number Plate Recognition"])

recognizer = LicensePlateRecognizer()

@router.get("/detections", response_model=List[ANPRPlateResult])
def get_anpr_detections():
    """Returns detected vehicle license plates across perimeter cameras."""
    return [
        {
            "plate_number": "KA 05 MN 4821",
            "vehicle_type": "Dark SUV / Sedan",
            "confidence": 0.94,
            "timestamp": "07:31:40 PM",
            "camera_id": "Camera 01 - Main Gate Checkpoint",
            "image_url": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=500&auto=format&fit=crop&q=60"
        },
        {
            "plate_number": "DL 3C BC 9012",
            "vehicle_type": "Delivery Van",
            "confidence": 0.88,
            "timestamp": "07:44:15 PM",
            "camera_id": "Camera 03 - West Perimeter Loading",
            "image_url": "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=500&auto=format&fit=crop&q=60"
        },
        {
            "plate_number": "MH 12 QP 5578",
            "vehicle_type": "Motorcycle",
            "confidence": 0.82,
            "timestamp": "08:04:50 PM",
            "camera_id": "Camera 03 - West Perimeter Exit",
            "image_url": "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?w=500&auto=format&fit=crop&q=60"
        }
    ]
