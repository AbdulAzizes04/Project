"""
Populate high-resolution 2D architectural blueprint plans into uploads/2d/
"""

import ssl
import urllib.request
import cv2
import numpy as np
from pathlib import Path
from config import UPLOADS_2D

BLUEPRINT_URLS = {
    "ground_floor_blueprint.jpg": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1200&auto=format&fit=crop",
    "modern_villa_architectural_plan.jpg": "https://images.unsplash.com/photo-1503387762-592deb58ef4e?q=80&w=1200&auto=format&fit=crop"
}

def generate_synthetic_2d_blueprint(filename: str, title: str):
    """Generates clean vector 2D architectural blueprint image as fallback/reference."""
    w, h = 1200, 900
    img = np.full((h, w, 3), (255, 255, 255), dtype=np.uint8) # Clean white paper background
    
    # Grid lines (Light Cyan Blueprint Grid)
    for x in range(0, w, 40):
        cv2.line(img, (x, 0), (x, h), (240, 248, 255), 1)
    for y in range(0, h, 40):
        cv2.line(img, (0, y), (w, y), (240, 248, 255), 1)
        
    # Draw Outer Plot Wall Boundary (Deep Navy / Cyan border)
    cv2.rectangle(img, (100, 100), (1100, 800), (15, 23, 42), 6)
    
    # Interior Room Division Walls
    cv2.line(img, (100, 450), (1100, 450), (15, 23, 42), 4) # Horizontal dividing wall
    cv2.line(img, (550, 100), (550, 450), (15, 23, 42), 4)  # Vert wall 1
    cv2.line(img, (450, 450), (450, 800), (15, 23, 42), 4)  # Vert wall 2
    cv2.line(img, (800, 450), (800, 800), (15, 23, 42), 4)  # Vert wall 3
    
    # Door Cutouts & Swing Arcs
    cv2.ellipse(img, (550, 280), (40, 40), 0, 0, 90, (8, 145, 178), 2)
    cv2.ellipse(img, (450, 600), (40, 40), 0, 90, 180, (8, 145, 178), 2)

    # Window Cutout double lines
    cv2.rectangle(img, (300, 95), (400, 105), (2, 132, 199), -1)
    cv2.rectangle(img, (750, 95), (850, 105), (2, 132, 199), -1)

    # Room Text Annotations
    cv2.putText(img, "LIVING HALL (20' x 16')", (180, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (8, 145, 178), 2)
    cv2.putText(img, "KITCHEN (14' x 14')", (680, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (8, 145, 178), 2)
    cv2.putText(img, "MASTER BEDROOM (16' x 14')", (130, 640), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (8, 145, 178), 2)
    cv2.putText(img, "BEDROOM 2 (14' x 14')", (500, 640), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (8, 145, 178), 2)
    cv2.putText(img, "BATHROOM (10' x 8')", (840, 640), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (8, 145, 178), 2)

    # Header Title
    cv2.rectangle(img, (100, 20), (1100, 80), (224, 242, 254), -1)
    cv2.rectangle(img, (100, 20), (1100, 80), (8, 145, 178), 2)
    cv2.putText(img, f"BUILDVERSE AI — {title}", (120, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (15, 23, 42), 2)

    target_p = UPLOADS_2D / filename
    cv2.imwrite(str(target_p), img)
    print(f"  [OK] Generated 2D Blueprint: {filename}")

def main():
    ctx = ssl._create_unverified_context()
    headers = {"User-Agent": "Mozilla/5.0"}
    
    print("Populating reference 2D architectural blueprints into uploads/2d/...")
    for filename, url in BLUEPRINT_URLS.items():
        try:
            target_path = UPLOADS_2D / filename
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=10) as response, open(target_path, "wb") as out_file:
                out_file.write(response.read())
            print(f"  [OK] Downloaded 2D plan: {filename}")
        except Exception:
            pass
            
    # Generate clean blueprint vector images
    generate_synthetic_2d_blueprint("ground_floor_blueprint.jpg", "GROUND FLOOR ARCHITECTURAL BLUEPRINT PLAN")
    generate_synthetic_2d_blueprint("first_floor_blueprint.jpg", "FIRST FLOOR ARCHITECTURAL BLUEPRINT PLAN")

if __name__ == "__main__":
    main()
