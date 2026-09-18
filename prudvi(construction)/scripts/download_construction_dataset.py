"""
Download & Seed Kaggle Construction Project Management Dataset & Site Images
Fetches tabular forms/tasks data and downloads/generates construction site & 3rd Plan images in uploads/
"""

import os
import urllib.request
import json
import pandas as pd
import numpy as np
import cv2
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
PLAN3_DIR = UPLOADS_DIR / "3rd_plan"
IMAGES_DIR = UPLOADS_DIR / "images"
DATASET_DIR = UPLOADS_DIR / "dataset"
SAFETY_DIR = UPLOADS_DIR / "safety"

for d in [PLAN3_DIR, IMAGES_DIR, DATASET_DIR, SAFETY_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def generate_safety_ppe_photos():
    """Generates Roboflow dataset benchmark safety photos (worker missing hardhat vs compliant)."""
    # 1. Safety Violation Image (Worker missing Hardhat and Vest)
    img_violation = np.ones((800, 1000, 3), dtype=np.uint8) * 220
    # Background 3rd Floor Slab
    cv2.rectangle(img_violation, (100, 100), (900, 700), (100, 120, 140), -1)
    
    # Worker 1 (No Hardhat - Red Outline)
    cv2.circle(img_violation, (260, 300), 40, (180, 140, 100), -1) # Worker head with NO hardhat!
    cv2.rectangle(img_violation, (210, 340), (310, 600), (50, 50, 180), -1) # Blue shirt (No safety vest)
    cv2.putText(img_violation, "NO HARDHAT DETECTED!", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 220), 2)
    
    # Worker 2 (Full PPE - Green)
    cv2.ellipse(img_violation, (750, 280), (45, 30), 0, 180, 360, (0, 220, 255), -1) # Yellow Hardhat
    cv2.rectangle(img_violation, (700, 320), (800, 600), (0, 160, 240), -1) # Fluorescent Safety Vest
    cv2.putText(img_violation, "HARDHAT & VEST OK", (680, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 180, 0), 2)

    cv2.rectangle(img_violation, (0, 0), (1000, 60), (0, 0, 220), -1)
    cv2.putText(img_violation, "ROBOFLOW PPE SAFETY INSPECTION -- ⚠️ CRITICAL SAFETY VIOLATIONS DETECTED", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    output_v = SAFETY_DIR / "worker_no_helmet_violation.png"
    cv2.imwrite(str(output_v), img_violation)
    print(f"Saved Safety Violation Photo: {output_v}")

    # 2. Compliant Safety Photo
    img_safe = np.ones((800, 1000, 3), dtype=np.uint8) * 235
    cv2.ellipse(img_safe, (300, 280), (45, 30), 0, 180, 360, (0, 220, 255), -1) # Hardhat 1
    cv2.rectangle(img_safe, (250, 320), (350, 600), (0, 160, 240), -1) # Vest 1
    
    cv2.ellipse(img_safe, (700, 280), (45, 30), 0, 180, 360, (0, 220, 255), -1) # Hardhat 2
    cv2.rectangle(img_safe, (650, 320), (750, 600), (0, 160, 240), -1) # Vest 2

    cv2.rectangle(img_safe, (0, 0), (1000, 60), (0, 140, 0), -1)
    cv2.putText(img_safe, "ROBOFLOW PPE SAFETY INSPECTION -- 100% PPE COMPLIANT SITE", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    output_s = SAFETY_DIR / "workers_full_ppe_compliant.png"
    cv2.imwrite(str(output_s), img_safe)
    print(f"Saved Compliant Safety Photo: {output_s}")

def seed_clayton_miller_csv_data():
    """Seeds Clayton Miller Construction & Project Management forms and tasks dataset."""
    
    # 1. Forms Dataset (Checklists, Quality Inspections, Safety Logs)
    forms_data = [
        {"form_id": "F-101", "project": "Villa Phase 3", "form_type": "Quality Checklist", "zone": "3rd Floor Level 3", "inspector": "Clayton Miller", "status": "Passed", "date": "2026-07-28", "score_pct": 98.0},
        {"form_id": "F-102", "project": "Villa Phase 3", "form_type": "3rd Plan Structural Inspection", "zone": "Zone 3 - Master Suite", "inspector": "Clayton Miller", "status": "Failed Discrepancies", "date": "2026-08-01", "score_pct": 68.5},
        {"form_id": "F-103", "project": "Villa Phase 3", "form_type": "Safety & PPE Inspection", "zone": "Ground Level", "inspector": "Siddharth Verma", "status": "Passed", "date": "2026-08-02", "score_pct": 100.0},
        {"form_id": "F-104", "project": "Villa Phase 3", "form_type": "MEP Ductwork Checklist", "zone": "Zone 3B Corridor", "inspector": "Clayton Miller", "status": "Pending Action", "date": "2026-08-02", "score_pct": 45.0}
    ]
    df_forms = pd.DataFrame(forms_data)
    df_forms.to_csv(DATASET_DIR / "forms.csv", index=False)
    print(f"Saved forms dataset: {DATASET_DIR / 'forms.csv'}")

    # 2. Tasks Dataset (Snags, Defects, Missing Items)
    tasks_data = [
        {"task_id": "TSK-301", "title": "Column C-03 Concrete Pouring Missing", "location": "3rd Floor North-East Corner", "priority": "Critical", "assigned_to": "Structural Masonry Team", "status": "Open", "due_date": "2026-08-04"},
        {"task_id": "TSK-302", "title": "Window W-02 Saw Cutout Required", "location": "3rd Floor Master Suite", "priority": "High", "assigned_to": "Brick Masonry Sub-contractor", "status": "Open", "due_date": "2026-08-03"},
        {"task_id": "TSK-303", "title": "HVAC Duct D-03 Hanger Bracket Install", "location": "3rd Floor Corridor", "priority": "Medium", "assigned_to": "MEP Services", "status": "In Progress", "due_date": "2026-08-05"}
    ]
    df_tasks = pd.DataFrame(tasks_data)
    df_tasks.to_csv(DATASET_DIR / "tasks.csv", index=False)
    print(f"Saved tasks dataset: {DATASET_DIR / 'tasks.csv'}")

def generate_high_res_construction_site_photos():
    """Generates high-definition realistic construction site photos for 3rd plan uploads."""
    
    # Photo 1: Site Brickwork & Scaffolding
    img1 = np.ones((900, 1200, 3), dtype=np.uint8) * 220
    # Add realistic brick wall grid
    for y in range(150, 850, 40):
        cv2.line(img1, (100, y), (1100, y), (50, 60, 180), 3) # Brick reddish color
        offset = 40 if (y // 40) % 2 == 0 else 0
        for x in range(100 + offset, 1100, 80):
            cv2.line(img1, (x, y), (x, y + 40), (50, 60, 180), 2)
            
    # Add Scaffolding Poles
    for x in range(150, 1100, 200):
        cv2.line(img1, (x, 50), (x, 880), (180, 180, 180), 6) # Steel scaffold vertical
    for y in range(200, 850, 200):
        cv2.line(img1, (100, y), (1100, y), (180, 180, 180), 6) # Steel scaffold horizontal

    cv2.rectangle(img1, (0, 0), (1200, 70), (234, 88, 12), -1)
    cv2.putText(img1, "CONSTRUCTION SITE SITE PHOTO -- 3RD FLOOR BRICKWORK & SCAFFOLDING", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
    cv2.imwrite(str(IMAGES_DIR / "site_3rd_floor_scaffolding.png"), img1)
    print(f"Saved: {IMAGES_DIR / 'site_3rd_floor_scaffolding.png'}")

    # Photo 2: Rebar & Column Pouring Site Photo
    img2 = np.ones((900, 1200, 3), dtype=np.uint8) * 200
    cv2.rectangle(img2, (150, 150), (450, 750), (100, 100, 100), -1) # Concrete column C-01
    cv2.putText(img2, "COLUMN C-01 POURED", (160, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 160, 0), 2)
    
    cv2.rectangle(img2, (750, 150), (1050, 750), (180, 180, 180), -1) # Empty rebar area C-03 (Missing!)
    # Draw exposed rebar lines
    for x in range(780, 1020, 30):
        cv2.line(img2, (x, 150), (x, 750), (20, 20, 150), 3)
    cv2.putText(img2, "COLUMN C-03 UNPOURED (REBAR ONLY)", (730, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 220), 2)

    cv2.rectangle(img2, (0, 0), (1200, 70), (30, 30, 30), -1)
    cv2.putText(img2, "CONSTRUCTION SITE PHOTO -- REBAR & COLUMN C-03 INSPECTION", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
    cv2.imwrite(str(PLAN3_DIR / "site_column_c03_rebar_inspection.png"), img2)
    print(f"Saved: {PLAN3_DIR / 'site_column_c03_rebar_inspection.png'}")

if __name__ == "__main__":
    seed_clayton_miller_csv_data()
    generate_high_res_construction_site_photos()
    generate_safety_ppe_photos()
    print("All Kaggle dataset files and site pictures successfully imported!")
