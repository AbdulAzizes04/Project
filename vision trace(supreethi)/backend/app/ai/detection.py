import os
import cv2
import numpy as np
from typing import List, Dict, Any, Tuple

class PersonDetector:
    def __init__(self, model_name: str = "yolov8n.pt", conf_thresh: float = 0.35):
        self.conf_thresh = conf_thresh
        self.model_name = model_name
        self._model = None
        self._tried_load = False

    def _get_model(self):
        if not self._tried_load:
            self._tried_load = True
            try:
                from ultralytics import YOLO
                self._model = YOLO(self.model_name)
            except Exception as e:
                print(f"[PersonDetector] YOLO init warning (OpenCV fallback enabled): {e}")
        return self._model

    def detect_frame(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect persons and vehicles in a single frame.
        Returns list of detections with bbox (norm x, y, w, h), conf, and class.
        """
        h, w = frame.shape[:2]
        detections = []

        model = self._get_model()
        if model is not None:
            try:
                results = model(frame, verbose=False, conf=self.conf_thresh)
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        cls_id = int(box.cls[0].item())
                        cls_name = r.names[cls_id]
                        conf = float(box.conf[0].item())
                        if cls_name in ["person", "car", "motorcycle", "bus", "truck"]:
                            x1, y1, x2, y2 = box.xyxy[0].tolist()
                            detections.append({
                                "class_name": cls_name,
                                "confidence": round(conf, 3),
                                "bbox_pixels": [int(x1), int(y1), int(x2 - x1), int(y2 - y1)],
                                "bbox_norm": [round(x1/w, 4), round(y1/h, 4), round((x2-x1)/w, 4), round((y2-y1)/h, 4)]
                            })
                return detections
            except Exception as e:
                print(f"[PersonDetector] Detection error: {e}")

        # Fallback heuristic detector using OpenCV HOG if YOLO is not available
        try:
            hog = cv2.HOGDescriptor()
            hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
            rects, weights = hog.detectMultiScale(frame, winStride=(8, 8), padding=(8, 8), scale=1.05)
            for (x, y, bw, bh), weight in zip(rects, weights):
                detections.append({
                    "class_name": "person",
                    "confidence": round(float(weight[0]) if hasattr(weight, '__iter__') else float(weight), 3),
                    "bbox_pixels": [int(x), int(y), int(bw), int(bh)],
                    "bbox_norm": [round(x/w, 4), round(y/h, 4), round(bw/w, 4), round(bh/h, 4)]
                })
        except Exception:
            pass

        return detections

    def draw_forensic_overlay(self, frame: np.ndarray, detections: List[Dict[str, Any]], track_id: int = None) -> np.ndarray:
        output = frame.copy()
        for det in detections:
            x, y, w, h = det["bbox_pixels"]
            label = det["class_name"].upper()
            conf = int(det["confidence"] * 100)
            
            color = (255, 230, 0) if label == "PERSON" else (0, 200, 255)
            line_len = min(20, w // 4, h // 4)
            t = 2
            cv2.rectangle(output, (x, y), (x + w, y + h), color, 1)
            cv2.line(output, (x, y), (x + line_len, y), color, t + 1)
            cv2.line(output, (x, y), (x, y + line_len), color, t + 1)
            cv2.line(output, (x + w, y), (x + w - line_len, y), color, t + 1)
            cv2.line(output, (x + w, y), (x + w, y + line_len), color, t + 1)
            cv2.line(output, (x, y + h), (x + line_len, y + h), color, t + 1)
            cv2.line(output, (x, y + h), (x, y + h - line_len), color, t + 1)
            cv2.line(output, (x + w, y + h), (x + w - line_len, y + h), color, t + 1)
            cv2.line(output, (x + w, y + h), (x + w, y + h - line_len), color, t + 1)

            display_text = f"TRACK #{track_id if track_id else det.get('track_id', '01')} | {label} {conf}%"
            cv2.rectangle(output, (x, y - 22), (x + 180, y), (20, 20, 30), -1)
            cv2.putText(output, display_text, (x + 4, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.42, color, 1, cv2.LINE_AA)
        return output
