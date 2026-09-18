"""
API Endpoints for Compression, Quantum Processing, Reconstruction, and Multi-Model Comparison.
"""

from pathlib import Path
import time
import cv2
import numpy as np
import torch
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from backend.config import (
    SAVED_MODELS_DIR,
    RESULTS_DIR,
    IMAGE_SIZE,
    DEVICE,
    MEDICAL_DISCLAIMER
)
from backend.database import get_connection, save_compression_run
from backend.preprocessing.image_processor import (
    preprocess_image,
    deprocess_image,
    generate_difference_heatmap
)
from backend.models.quantum_autoencoder import create_model
from backend.serialization.compressor import serialize_latent_to_qmc, deserialize_qmc_to_latent
from backend.evaluation.metrics import evaluate_reconstruction_all
from backend.evaluation.benchmark import compress_with_jpeg
from backend.utils.helpers import setup_logger

logger = setup_logger("API_Compression")
router = APIRouter(prefix="/api", tags=["Compression"])

COMPRESSED_DIR = RESULTS_DIR / "compressed"
RECON_DIR = RESULTS_DIR / "reconstructed"
HEATMAP_DIR = RESULTS_DIR / "heatmaps"

for d in [COMPRESSED_DIR, RECON_DIR, HEATMAP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Cache loaded models in memory for fast inference
_LOADED_MODELS: Dict[str, Any] = {}

def get_or_load_model(model_type: str):
    """Loads and caches PyTorch models from saved_models directory."""
    mtype = model_type.upper()
    if mtype in _LOADED_MODELS:
        return _LOADED_MODELS[mtype]

    model = create_model(mtype)
    ckpt_name = "classical_autoencoder.pth" if "CLASSICAL" in mtype else "hybrid_quantum_autoencoder.pth"
    ckpt_path = SAVED_MODELS_DIR / ckpt_name

    if ckpt_path.exists():
        state = torch.load(ckpt_path, map_location=DEVICE)
        model.load_state_dict(state["model_state_dict"])
        logger.info(f"Loaded weights from {ckpt_path}")
    else:
        logger.warning(f"Checkpoint not found at {ckpt_path}. Using initialized model weights.")

    model.to(DEVICE)
    model.eval()
    _LOADED_MODELS[mtype] = model
    return model

class CompressRequest(BaseModel):
    image_id: int
    model_type: str = "HYBRID_QUANTUM"  # 'CLASSICAL_AUTOENCODER', 'HYBRID_QUANTUM', or 'JPEG'

class CompressResponse(BaseModel):
    run_id: int
    image_id: int
    model_type: str
    original_size_bytes: int
    compressed_size_bytes: int
    compression_ratio: float
    storage_reduction_percent: float
    mse: float
    psnr: float
    ssim: float
    inference_time_ms: float
    original_url: str
    reconstructed_url: str
    heatmap_url: str
    compressed_file_url: str
    disclaimer: str

@router.post("/compress", response_model=CompressResponse)
async def compress_image(request: CompressRequest):
    """
    Executes compression on a registered image using Classical Autoencoder,
    Hybrid Quantum Model, or standard baseline JPEG.
    """
    # 1. Fetch image from database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM images WHERE id = ?", (request.image_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Image with ID {request.image_id} not found.")

    image_path = Path(row["original_path"])
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image file missing from storage.")

    # 2. Preprocess
    tensor, meta = preprocess_image(image_path)
    orig_np = deprocess_image(tensor)
    orig_bytes = row["original_size_bytes"]

    mtype = request.model_type.upper()
    timestamp = int(time.time() * 1000)

    # 3. Model execution
    if mtype == "JPEG":
        start_time = time.time()
        res_jpeg = compress_with_jpeg(orig_np, quality=25)
        recon_np = cv2.imdecode(
            cv2.imencode(".jpg", orig_np, [cv2.IMWRITE_JPEG_QUALITY, 25])[1],
            cv2.IMREAD_GRAYSCALE
        )
        latency_ms = (time.time() - start_time) * 1000.0

        # Save files
        comp_path = COMPRESSED_DIR / f"jpeg_{timestamp}.jpg"
        cv2.imwrite(str(comp_path), recon_np, [cv2.IMWRITE_JPEG_QUALITY, 25])
        comp_size = comp_path.stat().st_size
    else:
        model = get_or_load_model(mtype)
        start_time = time.time()
        with torch.no_grad():
            # Encode
            latent = model.encode(tensor.to(DEVICE))
            
            # Serialize to real on-disk .qmc file
            comp_path = COMPRESSED_DIR / f"{mtype.lower()}_{timestamp}.qmc"
            _, stats = serialize_latent_to_qmc(
                latent=latent,
                output_path=comp_path,
                model_type=mtype,
                target_shape=IMAGE_SIZE,
                quantize_mode="int8"
            )
            comp_size = stats["total_compressed_bytes"]

            # Deserialize from disk
            recovered_latent, _ = deserialize_qmc_to_latent(comp_path)
            
            # Decode
            recon_tensor = model.decode(recovered_latent.to(DEVICE))
            recon_np = deprocess_image(recon_tensor)
            latency_ms = (time.time() - start_time) * 1000.0

    # Save reconstructed image and difference heatmap
    recon_filename = f"recon_{timestamp}.png"
    recon_path = RECON_DIR / recon_filename
    cv2.imwrite(str(recon_path), recon_np)

    heatmap_np = generate_difference_heatmap(orig_np, recon_np)
    heatmap_filename = f"diff_{timestamp}.png"
    heatmap_path = HEATMAP_DIR / heatmap_filename
    cv2.imwrite(str(heatmap_path), heatmap_np)

    # Calculate final rigorous metrics
    metrics = evaluate_reconstruction_all(
        original=orig_np,
        reconstructed=recon_np,
        original_size_bytes=orig_bytes,
        compressed_size_bytes=comp_size,
        inference_time_ms=latency_ms
    )

    # Record run in SQLite
    run_record = {
        "image_id": request.image_id,
        "model_type": mtype,
        "compressed_file_path": str(comp_path),
        "reconstructed_image_path": str(recon_path),
        "original_size_bytes": orig_bytes,
        "compressed_size_bytes": comp_size,
        "compression_ratio": metrics["compression_ratio"],
        "storage_reduction_percent": metrics["storage_reduction_percent"],
        "mse": metrics["mse"],
        "psnr": metrics["psnr"],
        "ssim": metrics["ssim"],
        "inference_time_ms": metrics["inference_time_ms"]
    }
    run_id = save_compression_run(run_record)

    return CompressResponse(
        run_id=run_id,
        image_id=request.image_id,
        model_type=mtype,
        original_size_bytes=orig_bytes,
        compressed_size_bytes=comp_size,
        compression_ratio=metrics["compression_ratio"],
        storage_reduction_percent=metrics["storage_reduction_percent"],
        mse=metrics["mse"],
        psnr=metrics["psnr"],
        ssim=metrics["ssim"],
        inference_time_ms=metrics["inference_time_ms"],
        original_url=f"/media/uploads/{row['filename']}",
        reconstructed_url=f"/media/reconstructed/{recon_filename}",
        heatmap_url=f"/media/heatmaps/{heatmap_filename}",
        compressed_file_url=f"/media/compressed/{comp_path.name}",
        disclaimer=MEDICAL_DISCLAIMER
    )

@router.post("/compare-all")
async def compare_all_models(request: CompressRequest):
    """
    Executes JPEG, Classical Autoencoder, and Hybrid Quantum Autoencoder
    on the specified image simultaneously and returns comparative evaluation.
    """
    methods = ["JPEG", "CLASSICAL_AUTOENCODER", "HYBRID_QUANTUM"]
    results = []

    for m in methods:
        req = CompressRequest(image_id=request.image_id, model_type=m)
        res = await compress_image(req)
        results.append(res)

    return {
        "image_id": request.image_id,
        "comparisons": results,
        "disclaimer": MEDICAL_DISCLAIMER
    }
