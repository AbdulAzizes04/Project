"""
FastAPI Main Application — Thyroid Risk Assessment Platform
"""
import os, sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

# ── Ensure parent folders exist ───────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
for folder in ["uploads", "reports", "ml_models/saved_models", "datasets"]:
    (BASE_DIR / folder).mkdir(parents=True, exist_ok=True)

# ── DB + ML boot ──────────────────────────────────────────────────────────────
from database.db import init_db
from services.ml_service import ml_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    await ml_service.load_models()
    yield

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Thyroid Risk Assessment API",
    description="Patient-Specific Thyroid Risk Assessment Through Hybrid Explainable Machine Learning",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
uploads_path = str(BASE_DIR / "uploads")
reports_path = str(BASE_DIR / "reports")
app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")
app.mount("/reports", StaticFiles(directory=reports_path), name="reports")

# ── Routers ───────────────────────────────────────────────────────────────────
from routers import auth, patients, predictions, reports, admin, ocr, appointments

app.include_router(auth.router,        prefix="/api/auth",        tags=["Auth"])
app.include_router(patients.router,    prefix="/api/patients",    tags=["Patients"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["Predictions"])
app.include_router(reports.router,     prefix="/api/reports",     tags=["Reports"])
app.include_router(admin.router,       prefix="/api/admin",       tags=["Admin"])
app.include_router(ocr.router,         prefix="/api/ocr",         tags=["OCR"])
app.include_router(appointments.router,prefix="/api/appointments",tags=["Appointments"])


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "service": "Thyroid Risk Assessment API", "version": "1.0.0"}


@app.get("/api/health", tags=["Health"])
async def health():
    return {
        "status": "healthy",
        "models_loaded": ml_service.models_loaded,
        "db": "connected"
    }
