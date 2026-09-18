"""
VisionTrace AI — FastAPI Main Application
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database.database import init_db
from api import cases, analysis, chatbot, reports

app = FastAPI(
    title="VisionTrace AI",
    description="Intelligent Forensic Surveillance Platform",
    version="1.0.0",
)

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(cases.router)
app.include_router(analysis.router)
app.include_router(chatbot.router)
app.include_router(reports.router)

# Serve uploaded files as static (for CCTV player)
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.on_event("startup")
def on_startup():
    # Ensure DB directory exists
    db_dir = os.path.join(os.path.dirname(__file__), "database")
    os.makedirs(db_dir, exist_ok=True)
    init_db()
    print("[VisionTrace AI] Database initialised. System online.")


@app.get("/")
def health():
    return {"status": "online", "system": "VisionTrace AI", "version": "1.0.0"}


@app.get("/api/health")
def api_health():
    return {"status": "online", "message": "VisionTrace AI backend operational"}
