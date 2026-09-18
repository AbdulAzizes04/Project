"""
VisionTrace AI — Person Detector Service
Uses YOLOv8 for detection; falls back to demo simulation if unavailable.
"""
import os
import numpy as np
from typing import List, Dict, Any, Optional

# Try importing ultralytics (YOLOv8). If unavailable, use simulated detections.
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


class PersonDetector:
    """
    Wraps YOLOv8 for person detection. 
    Falls back to deterministic simulation when YOLOv8 is not installed.
    """

    MODEL_PATH = "yolov8n.pt"   # downloads automatically on first run

    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        if YOLO_AVAILABLE:
            try:
                self.model = YOLO(self.MODEL_PATH)
                print("[PersonDetector] YOLOv8 model loaded.")
            except Exception as e:
                print(f"[PersonDetector] Model load failed: {e}. Using demo mode.")
                self.model = None
        else:
            print("[PersonDetector] ultralytics not installed. Using demo simulation.")

    @property
    def is_real(self) -> bool:
        return self.model is not None

    def detect(self, frame: np.ndarray, conf_threshold: float = 0.4) -> List[Dict[str, Any]]:
        """
        Run detection on a single frame.
        Returns list of { class, confidence, bbox: [x1,y1,x2,y2] }
        """
        if self.model is not None:
            return self._detect_real(frame, conf_threshold)
        return self._detect_simulated(frame)

    def _detect_real(self, frame: np.ndarray, conf_threshold: float) -> List[Dict[str, Any]]:
        results = self.model(frame, classes=[0], conf=conf_threshold, verbose=False)
        detections = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                detections.append({
                    "class": "person",
                    "confidence": float(box.conf[0]),
                    "bbox": [x1, y1, x2, y2],
                })
        return detections

    def _detect_simulated(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Return 1-3 simulated person detections based on frame shape."""
        h, w = frame.shape[:2] if frame is not None else (480, 640)
        rng = np.random.default_rng(seed=int(w + h) % 100)
        num_persons = rng.integers(1, 4)
        detections = []
        for i in range(num_persons):
            bw = rng.integers(80, 200)
            bh = rng.integers(200, 380)
            bx = rng.integers(0, max(1, w - bw))
            by = rng.integers(0, max(1, h - bh))
            detections.append({
                "class": "person",
                "confidence": round(float(rng.uniform(0.72, 0.97)), 3),
                "bbox": [float(bx), float(by), float(bx + bw), float(by + bh)],
            })
        return detections

    def detect_batch(
        self, frames_data: List[Dict[str, Any]], conf_threshold: float = 0.4
    ) -> List[Dict[str, Any]]:
        """
        Run detection over a list of frame dicts.
        Returns enriched list with detections field.
        """
        results = []
        for fd in frames_data:
            frame = fd.get("frame")
            dets = self.detect(frame, conf_threshold)
            results.append({
                **fd,
                "detections": dets,
            })
        return results
