import cv2
import numpy as np
from typing import Dict, Any, Tuple

class MaskDetector:
    """
    Forensic Face Occlusion & Mask Detector.
    Evaluates whether a detected person's facial region is:
    - Visible
    - Partially Covered
    - Masked
    - Occluded

    CRITICAL FORENSIC RULE:
    If a subject is MASKED or OCCLUDED, the system NEVER hallucinates or attempts
    to reconstruct the hidden face. Instead, it activates the Alternative Forensic Pipeline:
    - Appearance & Clothing Signature
    - Body Silhouette & Height-to-Width Ratio
    - Pose Analysis
    - Gait Characteristic Extraction
    """
    def __init__(self):
        # We can use Haar cascade face detector or skin-tone ratio on upper head crop
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        except Exception:
            self.face_cascade = None

    def analyze_face_visibility(self, person_crop: np.ndarray) -> Dict[str, Any]:
        """
        Analyzes the upper portion of a person crop (head/face area).
        """
        if person_crop is None or person_crop.size == 0:
            return {
                "face_visibility": "Occluded",
                "alternative_pipeline_active": True,
                "confidence": 0.85,
                "reason": "Crop area unavailable or zero pixels"
            }

        ch, cw = person_crop.shape[:2]
        # Head/Face is typically top 25% of the person's bounding box
        head_crop = person_crop[0:int(ch * 0.28), :]

        if head_crop.size == 0 or head_crop.shape[0] < 10 or head_crop.shape[1] < 10:
            return {
                "face_visibility": "Partially Covered",
                "alternative_pipeline_active": True,
                "confidence": 0.78,
                "reason": "Resolution insufficient for reliable face biometric extraction"
            }

        # Check for visible face using cascade
        gray_head = cv2.cvtColor(head_crop, cv2.COLOR_BGR2GRAY)
        faces = []
        if self.face_cascade is not None:
            faces = self.face_cascade.detectMultiScale(gray_head, scaleFactor=1.1, minNeighbors=3, minSize=(15, 15))

        # Check skin color distribution in HSV
        hsv_head = cv2.cvtColor(head_crop, cv2.COLOR_BGR2HSV)
        # Skin tone range in HSV
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([25, 255, 255], dtype=np.uint8)
        skin_mask = cv2.inRange(hsv_head, lower_skin, upper_skin)
        skin_ratio = np.sum(skin_mask > 0) / (head_crop.shape[0] * head_crop.shape[1])

        # Color variance / dark fabric coverage
        # Many perpetrators wear dark balaclavas, black surgical masks, or medical blue masks
        lower_dark = np.array([0, 0, 0], dtype=np.uint8)
        upper_dark = np.array([180, 255, 60], dtype=np.uint8)
        dark_mask = cv2.inRange(hsv_head, lower_dark, upper_dark)
        dark_ratio = np.sum(dark_mask > 0) / (head_crop.shape[0] * head_crop.shape[1])

        lower_blue_mask = np.array([90, 50, 50], dtype=np.uint8)
        upper_blue_mask = np.array([130, 255, 255], dtype=np.uint8)
        blue_mask = cv2.inRange(hsv_head, lower_blue_mask, upper_blue_mask)
        blue_ratio = np.sum(blue_mask > 0) / (head_crop.shape[0] * head_crop.shape[1])

        if len(faces) > 0 and skin_ratio > 0.35:
            return {
                "face_visibility": "Visible",
                "alternative_pipeline_active": False,
                "confidence": 0.91,
                "skin_ratio": round(float(skin_ratio), 3),
                "reason": "Facial features detected with standard skin reflectance"
            }
        elif dark_ratio > 0.45 or blue_ratio > 0.20:
            return {
                "face_visibility": "Masked",
                "alternative_pipeline_active": True,
                "confidence": 0.93,
                "skin_ratio": round(float(skin_ratio), 3),
                "reason": "Facial region obscured by mask/cover. Activated gait and alternative appearance pipeline."
            }
        elif skin_ratio < 0.15:
            return {
                "face_visibility": "Partially Covered",
                "alternative_pipeline_active": True,
                "confidence": 0.82,
                "skin_ratio": round(float(skin_ratio), 3),
                "reason": "Low facial exposure or headwear occlusion detected"
            }
        else:
            return {
                "face_visibility": "Occluded",
                "alternative_pipeline_active": True,
                "confidence": 0.79,
                "skin_ratio": round(float(skin_ratio), 3),
                "reason": "Angle or illumination prevents definitive facial biometric read"
            }
