"""
Prepare Kaggle Construction & Project Management Sample Media
Generates sample 3rd Plan blueprints and site inspection photos in the uploads folder.
"""

import os
import cv2
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
PLAN_DIR = UPLOADS_DIR / "3rd_plan"
IMAGES_DIR = UPLOADS_DIR / "images"
FLOORPLANS_DIR = UPLOADS_DIR / "floorplans"

for d in [PLAN_DIR, IMAGES_DIR, FLOORPLANS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def create_3rd_plan_blueprint():
    """Generates a detailed 2D Blueprint image for Floor Plan 3 (3rd Plan)."""
    img = np.ones((800, 1000, 3), dtype=np.uint8) * 255
    
    # Blueprint grid background
    for x in range(0, 1000, 40):
        cv2.line(img, (x, 0), (x, 800), (240, 240, 240), 1)
    for y in range(0, 800, 40):
        cv2.line(img, (0, y), (1000, y), (240, 240, 240), 1)
        
    # Draw Outer Structure Wall (3rd Floor Plan)
    cv2.rectangle(img, (100, 100), (900, 700), (30, 30, 30), 4)
    
    # Draw Structural Columns (C-01 to C-09)
    columns = [
        (100, 100, "C-01"), (500, 100, "C-02"), (900, 100, "C-03 (MISSING IN SITE)"),
        (100, 400, "C-04"), (500, 400, "C-05"), (900, 400, "C-06"),
        (100, 700, "C-07"), (500, 700, "C-08"), (900, 700, "C-09")
    ]
    
    for cx, cy, label in columns:
        color = (0, 0, 220) if "MISSING" in label else (40, 40, 40)
        cv2.rectangle(img, (cx-15, cy-15), (cx+15, cy+15), color, -1)
        cv2.putText(img, label.split()[0], (cx-18, cy-22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
    # Rooms & Walls
    # Executive Suite / Bedroom 3
    cv2.rectangle(img, (100, 100), (500, 400), (60, 60, 60), 2)
    cv2.putText(img, "ZONE 3A: MASTER SUITE (3RD PLAN)", (130, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (234, 88, 12), 2)
    
    # Window cutout W-02
    cv2.line(img, (250, 100), (350, 100), (0, 180, 240), 6)
    cv2.putText(img, "WINDOW W-02", (240, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 140, 200), 2)
    
    # Zone 3B: HVAC & Electrical Corridor
    cv2.rectangle(img, (500, 100), (900, 400), (60, 60, 60), 2)
    cv2.putText(img, "ZONE 3B: HVAC CORRIDOR (3RD PLAN)", (520, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (234, 88, 12), 2)
    
    # HVAC Duct Line
    cv2.line(img, (530, 250), (870, 250), (200, 150, 0), 3, cv2.LINE_AA)
    cv2.putText(img, "HVAC DUCT D-03 (MISSING IN SITE)", (540, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 220), 2)
    
    # Header Title Banner
    cv2.rectangle(img, (0, 0), (1000, 70), (234, 88, 12), -1)
    cv2.putText(img, "BUILDVERSE AI -- 3RD FLOOR ARCHITECTURAL BLUEPRINT (PLAN #3)", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
    
    output_path = PLAN_DIR / "3rd_plan_blueprint.png"
    cv2.imwrite(str(output_path), img)
    print(f"Saved 3rd Plan Blueprint: {output_path}")

def create_3rd_plan_site_photo_missing():
    """Generates actual site inspection photo based on 3rd Plan with missing items."""
    img = np.ones((800, 1000, 3), dtype=np.uint8) * 230
    
    # Concrete floor texture
    noise = np.random.randint(0, 30, (800, 1000, 3), dtype=np.uint8)
    img = cv2.subtract(img, noise)
    
    # Brick wall in progress
    cv2.rectangle(img, (100, 100), (500, 400), (100, 120, 150), -1) # Masonry wall
    for y in range(120, 400, 30):
        cv2.line(img, (100, y), (500, y), (70, 85, 110), 2)
        
    # Support columns installed
    cv2.rectangle(img, (85, 85), (115, 115), (50, 50, 50), -1)
    cv2.putText(img, "C-01 VERIFIED", (30, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 150, 0), 2)
    
    cv2.rectangle(img, (485, 85), (515, 115), (50, 50, 50), -1)
    cv2.putText(img, "C-02 VERIFIED", (440, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 150, 0), 2)
    
    # Column C-03 (MISSING - rebar exposed only)
    cv2.circle(img, (900, 100), 12, (0, 0, 220), 3)
    cv2.line(img, (890, 90), (910, 110), (0, 0, 220), 3)
    cv2.line(img, (910, 90), (890, 110), (0, 0, 220), 3)
    cv2.putText(img, "C-03 MISSING!", (830, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 220), 2)
    
    # Window W-02 cutout missing (Solid brick wall instead)
    cv2.rectangle(img, (250, 100), (350, 150), (0, 0, 200), 2)
    cv2.putText(img, "W-02 NOT CUT OUT!", (220, 175), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 220), 2)
    
    # HVAC Duct D-03 missing
    cv2.rectangle(img, (530, 220), (870, 280), (200, 200, 200), -1)
    cv2.putText(img, "EMPTY DUCT SPACE (D-03 MISSING)", (540, 255), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 220), 2)

    # Title
    cv2.rectangle(img, (0, 0), (1000, 60), (30, 30, 30), -1)
    cv2.putText(img, "3RD PLAN ACTUAL SITE PHOTO -- DISCREPANCY & MISSING ITEMS DETECTED", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

    output_path = PLAN_DIR / "3rd_plan_site_missing_elements.png"
    cv2.imwrite(str(output_path), img)
    print(f"Saved 3rd Plan Site Photo (Missing Items): {output_path}")

def create_3rd_plan_site_photo_complete():
    """Generates site photo matching 3rd plan completely."""
    img = np.ones((800, 1000, 3), dtype=np.uint8) * 235
    
    # Walls & Columns
    cv2.rectangle(img, (100, 100), (900, 700), (100, 130, 160), 4)
    
    columns = [(100, 100), (500, 100), (900, 100), (100, 400), (500, 400), (900, 400)]
    for cx, cy in columns:
        cv2.rectangle(img, (cx-18, cy-18), (cx+18, cy+18), (0, 160, 0), -1)
        
    # Window W-02 Present
    cv2.rectangle(img, (250, 90), (350, 110), (0, 180, 240), -1)
    cv2.putText(img, "W-02 OK", (270, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 150, 0), 2)
    
    # HVAC Duct D-03 Installed
    cv2.rectangle(img, (530, 235), (870, 265), (200, 160, 0), -1)
    cv2.putText(img, "HVAC D-03 INSTALLED", (610, 255), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Title
    cv2.rectangle(img, (0, 0), (1000, 60), (0, 120, 0), -1)
    cv2.putText(img, "3RD PLAN ACTUAL SITE PHOTO -- 100% COMPLIANT WITH BLUEPRINT", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

    output_path = PLAN_DIR / "3rd_plan_site_complete.png"
    cv2.imwrite(str(output_path), img)
    print(f"Saved 3rd Plan Site Photo (Complete): {output_path}")

if __name__ == "__main__":
    create_3rd_plan_blueprint()
    create_3rd_plan_site_photo_missing()
    create_3rd_plan_site_photo_complete()
    print("Dataset media preparation complete!")
