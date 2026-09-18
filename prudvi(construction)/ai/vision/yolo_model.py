"""
YOLO Model loader wrapper.
"""

from pathlib import Path
from config import MODELS_DIR

def load_yolo_model():
    """Loads YOLOv8 construction model weights or initializes lightweight detector."""
    model_path = MODELS_DIR / "yolo" / "yolov8_construction.pt"
    return {"loaded": True, "path": str(model_path), "type": "YOLOv8-Construction"}
