"""
Evaluation Metrics Module.
Calculates MSE, PSNR, SSIM, Compression Ratio (CR), and Storage Reduction (%)
with rigorous mathematical correctness for medical grayscale images.
"""

import math
from typing import Dict, Any, Union
import numpy as np
import torch
from skimage.metrics import structural_similarity as ssim_fn

def calculate_mse(original: np.ndarray, reconstructed: np.ndarray) -> float:
    """
    Computes Mean Squared Error (MSE) between original and reconstructed images.
    Supports both float [0.0, 1.0] and uint8 [0, 255] ranges.
    """
    orig = np.asarray(original, dtype=np.float64)
    recon = np.asarray(reconstructed, dtype=np.float64)
    if orig.shape != recon.shape:
        raise ValueError(f"Shape mismatch in MSE calculation: {orig.shape} vs {recon.shape}")
    
    mse = float(np.mean((orig - recon) ** 2))
    return mse

def calculate_psnr(
    original: np.ndarray,
    reconstructed: np.ndarray,
    max_val: Union[float, int] = None
) -> float:
    """
    Computes Peak Signal-to-Noise Ratio (PSNR) in decibels (dB).
    Formula: PSNR = 10 * log10(MAX^2 / MSE)
    """
    orig = np.asarray(original, dtype=np.float64)
    recon = np.asarray(reconstructed, dtype=np.float64)
    
    if max_val is None:
        # Infer max intensity based on range
        max_val = 255.0 if orig.max() > 1.5 else 1.0

    mse = calculate_mse(orig, recon)
    if mse == 0:
        return 100.0  # Perfect reconstruction boundary
    
    psnr = 10.0 * math.log10((max_val ** 2) / mse)
    return float(psnr)

def calculate_ssim(
    original: np.ndarray,
    reconstructed: np.ndarray,
    max_val: Union[float, int] = None
) -> float:
    """
    Computes Structural Similarity Index Measure (SSIM) in [0.0, 1.0].
    Preserves structural luminance, contrast, and structural comparison.
    """
    orig = np.asarray(original, dtype=np.float64).squeeze()
    recon = np.asarray(reconstructed, dtype=np.float64).squeeze()

    if max_val is None:
        max_val = 255.0 if orig.max() > 1.5 else 1.0

    score = ssim_fn(orig, recon, data_range=max_val)
    return float(score)

def calculate_compression_ratio(original_size_bytes: int, compressed_size_bytes: int) -> float:
    """
    Formula: Compression Ratio = Original Size / Compressed Size
    """
    if compressed_size_bytes <= 0:
        raise ValueError("Compressed size must be greater than 0.")
    return float(original_size_bytes / compressed_size_bytes)

def calculate_storage_reduction(original_size_bytes: int, compressed_size_bytes: int) -> float:
    """
    Formula: Storage Reduction (%) = ((Original Size - Compressed Size) / Original Size) * 100
    """
    if original_size_bytes <= 0:
        raise ValueError("Original size must be greater than 0.")
    reduction = ((original_size_bytes - compressed_size_bytes) / original_size_bytes) * 100.0
    return float(reduction)

def evaluate_reconstruction_all(
    original: np.ndarray,
    reconstructed: np.ndarray,
    original_size_bytes: int,
    compressed_size_bytes: int,
    inference_time_ms: float = 0.0
) -> Dict[str, Any]:
    """
    Aggregates all evaluation metrics into a standardized dictionary.
    """
    mse = calculate_mse(original, reconstructed)
    psnr = calculate_psnr(original, reconstructed)
    ssim = calculate_ssim(original, reconstructed)
    cr = calculate_compression_ratio(original_size_bytes, compressed_size_bytes)
    sr = calculate_storage_reduction(original_size_bytes, compressed_size_bytes)

    return {
        "mse": round(mse, 6),
        "psnr": round(psnr, 2),
        "ssim": round(ssim, 4),
        "original_size_bytes": original_size_bytes,
        "compressed_size_bytes": compressed_size_bytes,
        "compression_ratio": round(cr, 2),
        "storage_reduction_percent": round(sr, 2),
        "inference_time_ms": round(inference_time_ms, 2)
    }
