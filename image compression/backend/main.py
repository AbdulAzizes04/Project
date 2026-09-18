"""
FastAPI Main Application Entrypoint for QuantumMedCompress.
Mounts REST routers, CORS middleware, and static media files for images and plots.
"""

import sys
from pathlib import Path

# Ensure root directory is on Python path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import (
    DATASETS_DIR,
    RESULTS_DIR,
    PLOTS_DIR,
    MEDICAL_DISCLAIMER
)
from backend.database import init_db
from backend.api.upload import router as upload_router
from backend.api.compression import router as compression_router
from backend.api.evaluation import router as evaluation_router
from backend.utils.helpers import setup_logger

logger = setup_logger("Main")

app = FastAPI(
    title="QuantumMedCompress API",
    description="Quantum-Enhanced AI Framework for Medical Image Compression and Evaluation",
    version="1.0.0"
)

# Enable CORS for React frontend (localhost:5173, localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static media directories
MEDIA_UPLOADS = DATASETS_DIR / "uploads"
MEDIA_UPLOADS.mkdir(parents=True, exist_ok=True)
MEDIA_SYNTHETIC = DATASETS_DIR / "synthetic_mri"
MEDIA_SYNTHETIC.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/media/uploads", StaticFiles(directory=str(MEDIA_UPLOADS)), name="uploads")
app.mount("/media/synthetic", StaticFiles(directory=str(MEDIA_SYNTHETIC)), name="synthetic")
app.mount("/media/reconstructed", StaticFiles(directory=str(RESULTS_DIR / "reconstructed")), name="reconstructed")
app.mount("/media/heatmaps", StaticFiles(directory=str(RESULTS_DIR / "heatmaps")), name="heatmaps")
app.mount("/media/compressed", StaticFiles(directory=str(RESULTS_DIR / "compressed")), name="compressed")
app.mount("/media/plots", StaticFiles(directory=str(PLOTS_DIR)), name="plots")

# Include Routers
app.include_router(upload_router)
app.include_router(compression_router)
app.include_router(evaluation_router)

@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("QuantumMedCompress API started successfully.")

@app.get("/")
def root():
    return {
        "project": "QuantumMedCompress",
        "description": "A Scalable Quantum-Enhanced AI Model for Medical Image Compression and Optimization",
        "status": "ONLINE",
        "disclaimer": MEDICAL_DISCLAIMER,
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
