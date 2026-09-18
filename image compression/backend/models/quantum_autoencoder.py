"""
Unified Autoencoder Architectures:
1. ClassicalAutoencoder (Baseline 2)
2. HybridQuantumAutoencoder (Proposed Quantum-Enhanced Framework)
Includes differentiable compound loss (MSE + Structural Similarity).
"""

from typing import Tuple, Dict, Any, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F

from backend.config import (
    LATENT_DIM,
    NUM_QUBITS,
    NUM_QUANTUM_LAYERS,
    SSIM_LOSS_WEIGHT,
    DEVICE
)
from backend.models.encoder import MedicalCNNEncoder
from backend.models.decoder import MedicalCNNDecoder
from backend.models.quantum_layer import QuantumFeatureLayer

class DifferentiableSSIMLoss(nn.Module):
    """
    Differentiable 2D SSIM loss for PyTorch tensors in [0, 1].
    Uses a standard 11x11 Gaussian window for isotropic structural comparison.
    """
    def __init__(self, window_size: int = 11, channel: int = 1):
        super().__init__()
        self.window_size = window_size
        self.channel = channel
        # 1D Gaussian kernel
        sigma = 1.5
        gauss = torch.Tensor([
            math.exp(-(x - window_size // 2) ** 2 / float(2 * sigma ** 2))
            for x in range(window_size)
        ])
        gauss = (gauss / gauss.sum()).unsqueeze(1)
        # 2D Gaussian window
        _2d_window = gauss.mm(gauss.t()).float().unsqueeze(0).unsqueeze(0)
        self.register_buffer("window", _2d_window.expand(channel, 1, window_size, window_size).contiguous())

    def forward(self, img1: torch.Tensor, img2: torch.Tensor) -> torch.Tensor:
        """Computes 1.0 - SSIM(img1, img2) for loss minimization."""
        mu1 = F.conv2d(img1, self.window, padding=self.window_size // 2, groups=self.channel)
        mu2 = F.conv2d(img2, self.window, padding=self.window_size // 2, groups=self.channel)

        mu1_sq = mu1.pow(2)
        mu2_sq = mu2.pow(2)
        mu1_mu2 = mu1 * mu2

        sigma1_sq = F.conv2d(img1 * img1, self.window, padding=self.window_size // 2, groups=self.channel) - mu1_sq
        sigma2_sq = F.conv2d(img2 * img2, self.window, padding=self.window_size // 2, groups=self.channel) - mu2_sq
        sigma12 = F.conv2d(img1 * img2, self.window, padding=self.window_size // 2, groups=self.channel) - mu1_mu2

        c1 = 0.01 ** 2
        c2 = 0.03 ** 2

        ssim_map = ((2 * mu1_mu2 + c1) * (2 * sigma12 + c2)) / (
            (mu1_sq + mu2_sq + c1) * (sigma1_sq + sigma2_sq + c2)
        )
        return 1.0 - ssim_map.mean()

import math  # Needed for Gaussian kernel exponent

class MedicalReconstructionLoss(nn.Module):
    """
    Combined Loss: Loss = MSE + lambda * (1 - SSIM)
    Balances coarse spatial pixel convergence with high-frequency anatomical edge fidelity.
    """
    def __init__(self, ssim_weight: float = SSIM_LOSS_WEIGHT):
        super().__init__()
        self.ssim_weight = ssim_weight
        self.mse_fn = nn.MSELoss()
        self.ssim_fn = DifferentiableSSIMLoss(window_size=11, channel=1)

    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> Tuple[torch.Tensor, Dict[str, float]]:
        mse = self.mse_fn(pred, target)
        ssim_loss = self.ssim_fn(pred, target)
        total = mse + self.ssim_weight * ssim_loss
        return total, {
            "loss": float(total.item()),
            "mse": float(mse.item()),
            "ssim_loss": float(ssim_loss.item())
        }

class ClassicalAutoencoder(nn.Module):
    """
    Baseline Classical Convolutional Autoencoder.
    Input -> CNN Encoder -> Latent Vector z (N=8) -> CNN Decoder -> Reconstruction
    """
    def __init__(self, latent_dim: int = LATENT_DIM):
        super().__init__()
        self.model_type = "CLASSICAL_AUTOENCODER"
        self.latent_dim = latent_dim
        self.encoder = MedicalCNNEncoder(latent_dim=latent_dim)
        self.decoder = MedicalCNNDecoder(latent_dim=latent_dim)

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """Maps input image to compact latent representation."""
        return self.encoder(x)

    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """Reconstructs medical image from latent representation."""
        return self.decoder(z)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        z = self.encode(x)
        x_recon = self.decode(z)
        return x_recon, z

class HybridQuantumAutoencoder(nn.Module):
    """
    Proposed Hybrid Quantum-Classical Medical Autoencoder.
    Input -> CNN Encoder -> Classical Latent z -> Parameterized Quantum Circuit Layer -> Enhanced Latent z_q -> CNN Decoder -> Reconstruction
    """
    def __init__(
        self,
        latent_dim: int = LATENT_DIM,
        num_qubits: int = NUM_QUBITS,
        num_layers: int = NUM_QUANTUM_LAYERS
    ):
        super().__init__()
        self.model_type = "HYBRID_QUANTUM"
        self.latent_dim = latent_dim
        self.num_qubits = num_qubits
        self.num_layers = num_layers

        self.encoder = MedicalCNNEncoder(latent_dim=latent_dim)
        self.quantum_layer = QuantumFeatureLayer(
            latent_dim=latent_dim,
            num_qubits=num_qubits,
            num_layers=num_layers
        )
        self.decoder = MedicalCNNDecoder(latent_dim=latent_dim)

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """Maps input image through CNN encoder and quantum variational circuit."""
        z_classical = self.encoder(x)
        z_quantum = self.quantum_layer(z_classical)
        return z_quantum

    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """Reconstructs medical image from quantum-enhanced latent vector."""
        return self.decoder(z)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        z = self.encode(x)
        x_recon = self.decode(z)
        return x_recon, z

def create_model(
    model_type: str = "HYBRID_QUANTUM",
    latent_dim: int = LATENT_DIM,
    num_qubits: int = NUM_QUBITS,
    num_layers: int = NUM_QUANTUM_LAYERS
) -> nn.Module:
    """Factory helper to instantiate either model family."""
    if model_type.upper() in ["CLASSICAL", "CLASSICAL_AUTOENCODER", "CLASSICAL_ONLY"]:
        return ClassicalAutoencoder(latent_dim=latent_dim)
    elif model_type.upper() in ["HYBRID", "HYBRID_QUANTUM", "QUANTUM"]:
        return HybridQuantumAutoencoder(
            latent_dim=latent_dim,
            num_qubits=num_qubits,
            num_layers=num_layers
        )
    else:
        raise ValueError(f"Unknown model type '{model_type}'. Choose 'CLASSICAL_AUTOENCODER' or 'HYBRID_QUANTUM'.")
