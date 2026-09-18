"""
Unit tests for Medical Image Preprocessing and Dataset Loading.
"""

import tempfile
from pathlib import Path
import numpy as np
import cv2
import torch
import pytest

from backend.preprocessing.image_processor import (
    validate_image_file,
    preprocess_image,
    deprocess_image,
    generate_difference_heatmap,
    generate_synthetic_medical_dataset,
    get_dataloaders,
    InvalidImageError
)
from backend.config import IMAGE_SIZE

def test_synthetic_dataset_and_validation():
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = generate_synthetic_medical_dataset(tmp_dir, num_samples=10)
        files = list(Path(out_path).glob("*.png"))
        assert len(files) == 10
        
        info = validate_image_file(files[0])
        assert info["valid"] is True
        assert info["dimensions"] == (64, 64)
        assert info["size_bytes"] > 0

def test_preprocess_and_deprocess():
    # Create test dummy grayscale image
    dummy = np.random.randint(0, 256, (128, 128), dtype=np.uint8)
    tensor, meta = preprocess_image(dummy)
    
    # Check tensor properties
    assert isinstance(tensor, torch.Tensor)
    assert tensor.shape == (1, 1, IMAGE_SIZE[0], IMAGE_SIZE[1])
    assert tensor.dtype == torch.float32
    assert tensor.min() >= 0.0
    assert tensor.max() <= 1.0
    
    # Deprocess back
    reconstructed_uint8 = deprocess_image(tensor)
    assert isinstance(reconstructed_uint8, np.ndarray)
    assert reconstructed_uint8.shape == IMAGE_SIZE
    assert reconstructed_uint8.dtype == np.uint8

def test_difference_heatmap():
    img1 = np.full((64, 64), 50, dtype=np.uint8)
    img2 = np.full((64, 64), 100, dtype=np.uint8)
    heatmap = generate_difference_heatmap(img1, img2)
    assert heatmap.shape == (64, 64, 3)
    assert heatmap.dtype == np.uint8

def test_dataloaders():
    with tempfile.TemporaryDirectory() as tmp_dir:
        generate_synthetic_medical_dataset(tmp_dir, num_samples=20)
        train_l, val_l, test_l = get_dataloaders(Path(tmp_dir), batch_size=4)
        
        batch = next(iter(train_l))
        assert batch.shape == (4, 1, 64, 64)
        assert batch.dtype == torch.float32

def test_invalid_image_handling():
    with tempfile.TemporaryDirectory() as tmp_dir:
        fake_file = Path(tmp_dir) / "corrupt.txt"
        fake_file.write_text("not an image")
        with pytest.raises(InvalidImageError):
            validate_image_file(fake_file)
