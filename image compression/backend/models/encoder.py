"""
Classical CNN Encoder for Medical Images.
Transforms standardized 64x64 grayscale images into a compact continuous latent vector.
"""

import torch
import torch.nn as nn
from backend.config import LATENT_DIM

class MedicalCNNEncoder(nn.Module):
    """
    Hierarchical convolutional encoder mapping (B, 1, 64, 64) -> (B, latent_dim).
    Uses LeakyReLU activations and BatchNorm for stable convergence.
    """
    def __init__(self, latent_dim: int = LATENT_DIM):
        super().__init__()
        self.latent_dim = latent_dim

        # Feature extraction layers
        self.conv1 = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(16),
            nn.LeakyReLU(0.2, inplace=True),
            nn.MaxPool2d(2, 2)  # (B, 16, 32, 32)
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(32),
            nn.LeakyReLU(0.2, inplace=True),
            nn.MaxPool2d(2, 2)  # (B, 32, 16, 16)
        )
        self.conv3 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.2, inplace=True),
            nn.MaxPool2d(2, 2)  # (B, 64, 8, 8)
        )
        self.conv4 = nn.Sequential(
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.2, inplace=True),
            nn.AdaptiveAvgPool2d((4, 4))  # (B, 64, 4, 4)
        )

        # Bottleneck projection
        self.fc_latent = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 4 * 4, latent_dim),
            nn.Tanh()  # Bounds latent variables to [-1.0, 1.0] for stable angle embedding
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        x: (B, 1, 64, 64) in [0.0, 1.0]
        returns: (B, latent_dim) in [-1.0, 1.0]
        """
        features = self.conv1(x)
        features = self.conv2(features)
        features = self.conv3(features)
        features = self.conv4(features)
        latent = self.fc_latent(features)
        return latent
