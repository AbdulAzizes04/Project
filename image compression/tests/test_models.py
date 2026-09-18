"""
Unit tests for Classical and Hybrid Quantum Autoencoder models.
"""

import torch
import pytest

from backend.models.quantum_autoencoder import (
    ClassicalAutoencoder,
    HybridQuantumAutoencoder,
    MedicalReconstructionLoss,
    create_model
)
from backend.config import LATENT_DIM, IMAGE_SIZE

def test_classical_autoencoder_shapes():
    model = ClassicalAutoencoder(latent_dim=LATENT_DIM)
    x = torch.rand(2, 1, IMAGE_SIZE[0], IMAGE_SIZE[1])
    
    recon, z = model(x)
    assert z.shape == (2, LATENT_DIM)
    assert recon.shape == (2, 1, IMAGE_SIZE[0], IMAGE_SIZE[1])
    assert recon.min() >= 0.0
    assert recon.max() <= 1.0

def test_hybrid_quantum_autoencoder_shapes():
    model = HybridQuantumAutoencoder(latent_dim=LATENT_DIM, num_qubits=4, num_layers=2)
    x = torch.rand(2, 1, IMAGE_SIZE[0], IMAGE_SIZE[1])
    
    recon, z = model(x)
    assert z.shape == (2, LATENT_DIM)
    assert recon.shape == (2, 1, IMAGE_SIZE[0], IMAGE_SIZE[1])
    assert recon.min() >= 0.0
    assert recon.max() <= 1.0

def test_medical_reconstruction_loss_gradients():
    loss_fn = MedicalReconstructionLoss(ssim_weight=0.15)
    pred = torch.rand(2, 1, 64, 64, requires_grad=True)
    target = torch.rand(2, 1, 64, 64)
    
    loss, details = loss_fn(pred, target)
    assert "mse" in details
    assert "ssim_loss" in details
    assert loss.item() > 0
    
    loss.backward()
    assert pred.grad is not None
    assert not torch.isnan(pred.grad).any()

def test_factory_creation():
    m1 = create_model("CLASSICAL_AUTOENCODER")
    m2 = create_model("HYBRID_QUANTUM")
    assert isinstance(m1, ClassicalAutoencoder)
    assert isinstance(m2, HybridQuantumAutoencoder)
