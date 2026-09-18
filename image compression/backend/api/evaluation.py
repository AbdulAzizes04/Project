"""
API Endpoints for Analytics, Experiments History, Dashboard Metrics, and Model Specifications.
"""

from pathlib import Path
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd

from backend.config import (
    LATENT_DIM,
    NUM_QUBITS,
    NUM_QUANTUM_LAYERS,
    QUANTUM_DEVICE,
    IMAGE_SIZE,
    DEVICE,
    MEDICAL_DISCLAIMER,
    TABLES_DIR,
    PLOTS_DIR
)
from backend.database import (
    get_connection,
    get_recent_compression_runs,
    get_dashboard_summary
)

router = APIRouter(prefix="/api", tags=["Evaluation & Analytics"])

class ModelInfoResponse(BaseModel):
    model_name: str
    image_input_size: list
    channels: int
    latent_dimension: int
    number_of_qubits: int
    quantum_circuit_layers: int
    quantum_device_backend: str
    classical_backbone: str
    execution_device: str
    disclaimer: str

@router.get("/model-info", response_model=ModelInfoResponse)
async def get_model_info():
    """Returns technical architecture specifications of the quantum-classical compression engine."""
    return ModelInfoResponse(
        model_name="QuantumMedCompress Hybrid Framework",
        image_input_size=list(IMAGE_SIZE),
        channels=1,
        latent_dimension=LATENT_DIM,
        number_of_qubits=NUM_QUBITS,
        quantum_circuit_layers=NUM_QUANTUM_LAYERS,
        quantum_device_backend=QUANTUM_DEVICE,
        classical_backbone="4-Layer CNN Encoder + 4-Layer Transposed CNN Decoder",
        execution_device=DEVICE,
        disclaimer=MEDICAL_DISCLAIMER
    )

@router.get("/dashboard")
async def get_dashboard():
    """Returns aggregate summary metrics for the frontend dashboard cards."""
    summary = get_dashboard_summary()
    summary["disclaimer"] = MEDICAL_DISCLAIMER
    return summary

@router.get("/results")
async def get_results(limit: int = 25):
    """Returns historical list of compression runs with full metrics."""
    runs = get_recent_compression_runs(limit=limit)
    return {
        "count": len(runs),
        "results": runs,
        "disclaimer": MEDICAL_DISCLAIMER
    }

@router.get("/experiments")
async def get_experiments():
    """Returns training run experiments logged in database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM experiments ORDER BY completed_at DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {
        "count": len(rows),
        "experiments": rows,
        "disclaimer": MEDICAL_DISCLAIMER
    }

@router.get("/benchmark-data")
async def get_benchmark_data():
    """Returns latest benchmark table as JSON for frontend comparison charts."""
    csv_file = TABLES_DIR / "benchmark_comparison.csv"
    if not csv_file.exists():
        return {"data": [], "message": "Benchmark not run yet."}
    
    df = pd.read_csv(csv_file)
    return {
        "data": df.to_dict(orient="records"),
        "disclaimer": MEDICAL_DISCLAIMER
    }
