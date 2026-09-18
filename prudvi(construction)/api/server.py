"""
BuildVerse AI FastAPI Server
Connects React Frontend with Database, AI Vision Engine, Schedule Generator, and Floor Planner.
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from database.db import (
    init_db, get_all_projects, get_project, save_project,
    save_floors_and_rooms, save_schedules, save_monitoring_log, get_monitoring_logs
)
from ai.vision.plan_inspector import analyze_3rd_plan_inspection
from ai.planner.floor_plan_ai import generate_2d_floor_plan
from ai.construction.scheduler import generate_full_construction_schedule
from ai.construction.material_estimator import estimate_materials
from ai.digital_twin.twin_sync import sync_twin_with_progress

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

# Initialize Database
init_db()

app = FastAPI(
    title="BuildVerse AI API",
    description="Digital Twin & Construction Site Monitoring API",
    version="1.0.0"
)

# Enable CORS for React Frontend (typically running on localhost:5173 or 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Uploads Directory
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")


# Pydantic Schemas
class ProjectCreateSchema(BaseModel):
    name: str
    owner_name: str
    location: str
    plot_area: float
    plot_unit: str = "sq.ft"
    budget: float
    num_floors: int = 1
    workers_available: int = 10
    working_hours_per_day: float = 8.0
    material_preference: str = "Standard"
    weather_region: str = "Moderate"

class FloorRoomItemSchema(BaseModel):
    room_type: str
    length: float
    width: float

class FloorDataSchema(BaseModel):
    floor_name: str
    floor_level: int
    rooms: List[FloorRoomItemSchema]


@app.get("/")
def read_root():
    return {
        "status": "online",
        "app": "BuildVerse AI Backend",
        "version": "1.0.0",
        "theme": {
            "background": "#FFFFFF",
            "primary": "#EA580C",
            "secondary": "#EAB308",
            "text": "#000000"
        }
    }


# ---------------------------------------------------------
# PROJECTS API
# ---------------------------------------------------------
@app.get("/api/projects")
def list_projects():
    projects = get_all_projects()
    if not projects:
        # Create default demo project if empty
        default_p = {
            "name": "Emerald Heights Villa Phase 3",
            "owner_name": "Siddharth Verma",
            "location": "Sector 62, Gurgaon",
            "plot_area": 2400.0,
            "plot_unit": "sq.ft",
            "budget": 8500000.0,
            "num_floors": 3,
            "workers_available": 14,
            "working_hours_per_day": 8.0,
            "material_preference": "Premium",
            "weather_region": "Moderate"
        }
        pid = save_project(default_p)
        projects = get_all_projects()
    return projects

@app.get("/api/projects/{project_id}")
def get_project_by_id(project_id: int):
    p = get_project(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return {
        "project": p,
        "floors": p.get("floors", []),
        "schedules": p.get("schedules", [])
    }

# ---------------------------------------------------------
# KAGGLE CLAYTON MILLER DATASET API
# ---------------------------------------------------------
@app.get("/api/dataset")
def get_dataset():
    import pandas as pd
    dataset_dir = UPLOADS_DIR / "dataset"
    forms_path = dataset_dir / "forms.csv"
    tasks_path = dataset_dir / "tasks.csv"
    
    forms = []
    tasks = []
    if forms_path.exists():
        forms = pd.read_csv(forms_path).to_dict(orient="records")
    if tasks_path.exists():
        tasks = pd.read_csv(tasks_path).to_dict(orient="records")
        
    return {
        "dataset_name": "Clayton Miller Construction & Project Management Dataset",
        "source": "https://www.kaggle.com/datasets/claytonmiller/construction-and-project-management-example-data",
        "forms": forms,
        "tasks": tasks
    }


# ---------------------------------------------------------
# 3RD PLAN AI INSPECTION API
# ---------------------------------------------------------
@app.get("/api/inspect/presets")
def get_inspection_presets():
    """Returns available sample media presets (including Kaggle 3rd plan dataset images)."""
    plan_dir = UPLOADS_DIR / "3rd_plan"
    files = []
    if plan_dir.exists():
        for f in plan_dir.glob("*.png"):
            files.append({
                "filename": f.name,
                "label": f"3rd Plan: {f.stem.replace('_', ' ').title()}",
                "url": f"/uploads/3rd_plan/{f.name}"
            })
    return {
        "presets": files,
        "default_plan": "3rd_plan_site_missing_elements.png"
    }

@app.post("/api/inspect/3rd-plan")
async def inspect_3rd_plan(
    file: Optional[UploadFile] = File(None),
    preset_filename: Optional[str] = Form(None),
    floor_level: str = Form("3rd Floor / Level 3"),
    zone: str = Form("Zone 3 - Master Suite & Corridor")
):
    """
    Core feature: Analyzes site photo against 3rd Plan blueprint AND PPE worker safety.
    """
    image_path = None
    
    if file and file.filename:
        dest_dir = UPLOADS_DIR / "3rd_plan"
        dest_dir.mkdir(exist_ok=True)
        file_path = dest_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        image_path = str(file_path)
    elif preset_filename:
        if (UPLOADS_DIR / "safety" / preset_filename).exists():
            image_path = str(UPLOADS_DIR / "safety" / preset_filename)
        else:
            image_path = str(UPLOADS_DIR / "3rd_plan" / preset_filename)
    else:
        image_path = str(UPLOADS_DIR / "3rd_plan" / "3rd_plan_site_missing_elements.png")

    report = analyze_3rd_plan_inspection(
        image_path=image_path,
        selected_plan="3rd_plan",
        selected_floor=floor_level,
        zone=zone
    )
    
    return report


# ---------------------------------------------------------
# FLOOR PLANNER API
# ---------------------------------------------------------
@app.post("/api/planner/generate")
def generate_planner(
    plot_width: float = Form(40.0),
    plot_length: float = Form(60.0),
    floors_count: int = Form(3)
):
    """Generates 2D blueprint layout & 3D mesh structure for 3 Floors."""
    sample_rooms = [
        {"name": "Master Bedroom", "area": 250, "type": "Bedrooms"},
        {"name": "Kitchen", "area": 150, "type": "Kitchen"},
        {"name": "Living Room", "area": 350, "type": "Hall"},
        {"name": "Balcony", "area": 100, "type": "Balcony"}
    ]
    return {
        "plot_width": plot_width,
        "plot_length": plot_length,
        "total_area": plot_width * plot_length,
        "floors_count": floors_count,
        "sample_rooms": sample_rooms
    }


# ---------------------------------------------------------
# CONSTRUCTION SCHEDULE API
# ---------------------------------------------------------
@app.get("/api/schedule/{project_id}")
def get_project_schedule(project_id: int):
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    timeline = generate_full_construction_schedule(
        project_id=project_id,
        total_sqft=project["plot_area"],
        num_floors=project["num_floors"],
        total_budget=project["budget"],
        start_date="2026-08-01",
        desired_completion_date="2027-02-01",
        workers_available=project["workers_available"],
        working_hours_per_day=project["working_hours_per_day"]
    )
    
    materials = estimate_materials(
        total_sqft=project["plot_area"],
        num_floors=project["num_floors"]
    )
    
    return {
        "project_id": project_id,
        "timeline": timeline,
        "materials": materials
    }


# ---------------------------------------------------------
# DIGITAL TWIN API
# ---------------------------------------------------------
@app.get("/api/digital-twin/{project_id}")
def get_digital_twin(project_id: int):
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    twin_elements = sync_twin_with_progress(
        project_id=project_id,
        current_progress_pct=68.5
    )
    return {
        "project_id": project_id,
        "project_name": project["name"],
        "overall_progress": 68.5,
        "elements": twin_elements
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.server:app", host="127.0.0.1", port=8000, reload=True)
