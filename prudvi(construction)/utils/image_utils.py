"""
OpenCV Image processing, overlay, and engineering site inspection callout annotations.
"""

import cv2
import numpy as np
from PIL import Image
from typing import Tuple, List, Dict, Any

def load_cv_image(image_path: str) -> np.ndarray:
    """Loads an image into OpenCV numpy format."""
    img = cv2.imread(image_path)
    if img is None:
        img = np.zeros((720, 1280, 3), dtype=np.uint8)
        img[:] = (248, 250, 252)
        cv2.putText(img, "Construction Site Photo Scan", (50, 360), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (8, 145, 178), 2)
    return img

def draw_engineering_callout(
    img: np.ndarray,
    box: Tuple[int, int, int, int],
    title: str,
    subtitle: str,
    status_type: str = "completed"
):
    """Draws professional engineering site inspection callout badge on image."""
    x1, y1, x2, y2 = box
    
    colors = {
        "completed": ((16, 185, 129), (209, 250, 229), (6, 95, 70)),     # Green BGR
        "in_progress": ((8, 145, 178), (224, 242, 254), (15, 23, 42)),   # Cyan BGR
        "warning": ((14, 165, 233), (254, 243, 199), (146, 64, 14)),     # Yellow BGR
        "not_started": ((239, 68, 68), (254, 226, 226), (153, 27, 27))   # Red BGR
    }
    
    border_color, bg_color, text_color = colors.get(status_type, colors["in_progress"])
    
    # Structural zone outline box
    cv2.rectangle(img, (x1, y1), (x2, y2), border_color, 3)
    
    # Engineering Callout Badge Label Header
    badge_w = min(420, x2 - x1 + 40)
    badge_h = 44
    bx1 = max(10, x1)
    by1 = max(10, y1 - badge_h - 5)
    bx2 = bx1 + badge_w
    by2 = by1 + badge_h
    
    # Badge background card
    overlay = img.copy()
    cv2.rectangle(overlay, (bx1, by1), (bx2, by2), bg_color, -1)
    cv2.addWeighted(overlay, 0.9, img, 0.1, 0, img)
    cv2.rectangle(img, (bx1, by1), (bx2, by2), border_color, 2)
    
    # Text lines
    cv2.putText(img, title, (bx1 + 10, by1 + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.48, text_color, 2)
    cv2.putText(img, subtitle, (bx1 + 10, by1 + 36), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (71, 85, 105), 1)

def generate_engineering_site_overlay(
    img: np.ndarray,
    room_name: str = "Balcony",
    completion_pct: float = 48.0,
    current_activity: str = "Brick Masonry Work"
) -> np.ndarray:
    """Generates a professional Virtual Site Engineer inspection overlay with meaningful callout labels."""
    h, w, _ = img.shape
    result = img.copy()
    
    # Define primary inspection callouts
    callouts = [
        {
            "box": (int(w*0.25), int(h*0.35), int(w*0.85), int(h*0.90)),
            "title": f"🟢 {room_name} - {current_activity} ({completion_pct:.0f}% Complete)",
            "subtitle": f"Est Remaining: 3 Days | Next: Wall Plastering",
            "status": "in_progress"
        },
        {
            "box": (int(w*0.05), int(h*0.15), int(w*0.30), int(h*0.75)),
            "title": "🔵 Column C3 - Structural Concrete (100% Completed)",
            "subtitle": "Cured & Verified | Load Bearing Certified",
            "status": "completed"
        },
        {
            "box": (int(w*0.55), int(h*0.45), int(w*0.75), int(h*0.75)),
            "title": "🔴 Window Opening - Masonry Cutout (Not Constructed)",
            "subtitle": "Pending Brick Layer Queue | Est: 1 Day",
            "status": "not_started"
        },
        {
            "box": (int(w*0.30), int(h*0.05), int(w*0.90), int(h*0.25)),
            "title": "🟠 Wall Plastering Zone - Next Phase (0% Pending)",
            "subtitle": "Scheduled Start: 2 August | Duration: 2 Days",
            "status": "warning"
        }
    ]
    
    for c in callouts:
        draw_engineering_callout(result, c["box"], c["title"], c["subtitle"], c["status"])
        
    return result

def convert_cv_to_pil(cv_img: np.ndarray) -> Image.Image:
    """Converts OpenCV BGR image to PIL RGB image."""
    rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)
