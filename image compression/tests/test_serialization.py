"""
Tests for binary .qmc serialization, quantization, and round-trip consistency.
"""

import tempfile
from pathlib import Path
import numpy as np
import torch
import pytest

from backend.serialization.compressor import (
    serialize_latent_to_qmc,
    deserialize_qmc_to_latent,
    CorruptedQMCFileError
)

def test_qmc_serialization_roundtrip():
    with tempfile.TemporaryDirectory() as tmp_dir:
        qmc_path = Path(tmp_dir) / "test_sample.qmc"
        
        # Simulated latent vector (1, 8)
        original_latent = torch.tensor([[-0.85, -0.3, 0.12, 0.45, -0.1, 0.92, -0.4, 0.65]], dtype=torch.float32)
        
        saved_file, stats = serialize_latent_to_qmc(
            latent=original_latent,
            output_path=qmc_path,
            model_type="HYBRID_QUANTUM",
            target_shape=(64, 64),
            quantize_mode="int8"
        )
        
        assert saved_file.exists()
        assert stats["total_compressed_bytes"] > 0
        # Check that file size is tiny (approx 30-40 bytes)
        assert stats["total_compressed_bytes"] < 100
        
        # Deserialize
        recovered_latent, meta = deserialize_qmc_to_latent(saved_file)
        
        assert recovered_latent.shape == (1, 8)
        assert meta["model_type"] == "HYBRID_QUANTUM"
        assert meta["target_shape"] == (64, 64)
        
        # Max quantization error for 8-bit quantization across [-1, 1] is <= 2.0 / 255 = ~0.008
        diff = torch.abs(original_latent - recovered_latent).max().item()
        assert diff < 0.02

def test_corrupted_file_handling():
    with tempfile.TemporaryDirectory() as tmp_dir:
        fake_file = Path(tmp_dir) / "corrupt.qmc"
        fake_file.write_bytes(b"BADHEADER1234567890")
        with pytest.raises(CorruptedQMCFileError):
            deserialize_qmc_to_latent(fake_file)
