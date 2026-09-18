"""
Unit tests for evaluation metrics: MSE, PSNR, SSIM, CR, and Storage Reduction.
"""

import numpy as np
import pytest

from backend.evaluation.metrics import (
    calculate_mse,
    calculate_psnr,
    calculate_ssim,
    calculate_compression_ratio,
    calculate_storage_reduction,
    evaluate_reconstruction_all
)

def test_identical_image_metrics():
    img = np.random.randint(0, 256, (64, 64), dtype=np.uint8)
    
    mse = calculate_mse(img, img)
    assert mse == 0.0
    
    psnr = calculate_psnr(img, img, max_val=255.0)
    assert psnr == 100.0  # Perfect ceiling
    
    ssim = calculate_ssim(img, img, max_val=255.0)
    assert pytest.approx(ssim, 1e-4) == 1.0

def test_compression_ratio_and_storage_reduction():
    orig_bytes = 4096
    comp_bytes = 64
    
    cr = calculate_compression_ratio(orig_bytes, comp_bytes)
    assert cr == 64.0  # 4096 / 64
    
    sr = calculate_storage_reduction(orig_bytes, comp_bytes)
    assert sr == pytest.approx(98.4375, 0.01)

def test_evaluate_reconstruction_all():
    img1 = np.full((64, 64), 100, dtype=np.uint8)
    img2 = np.full((64, 64), 105, dtype=np.uint8)
    
    results = evaluate_reconstruction_all(
        original=img1,
        reconstructed=img2,
        original_size_bytes=4096,
        compressed_size_bytes=128,
        inference_time_ms=12.5
    )
    
    assert results["mse"] == 25.0
    assert results["psnr"] > 30.0
    assert results["compression_ratio"] == 32.0
    assert results["storage_reduction_percent"] > 90.0
