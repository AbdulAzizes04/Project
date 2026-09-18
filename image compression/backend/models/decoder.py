"""
Classical CNN Decoder for Medical Images.
Reconstructs standardized 64x64 grayscale images from a compact latent vector.
"""

import torch
import torch.nn as nn
from backend.config import LATENT_DIM

class MedicalCNNDecoder(nn.Module):
    """
    Transposed convolutional decoder mapping (B, latent_dim) -> (B, 1, 64, 64).
    Uses Sigmoid activation at the final layer to guarantee output pixel intensities in [0.0, 1.0].
    """
    def __init__(self, latent_dim: int = LATENT_DIM):
        super().__init__()
        self.latent_dim = latent_dim

        # Expand latent vector into spatial feature maps
        self.fc_expand = nn.Sequential(
            nn.Linear(latent_dim, 64 * 4 * 4),
            nn.LeakyReLU(0.2, inplace=True)
        )

        # Transposed convolutional upsampling layers
        self.deconv1 = nn.Sequential(
            nn.ConvTranspose2d(64, 64, kernel_size=4, stride=2, padding=1),  # (B, 64, 8, 8)
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.2, inplace=True)
        )
        self.deconv2 = nn.Sequential(
            nn.ConvTranspose2d(64, 32, kernel_size=4, stride=2, padding=1),  # (B, 32, 16, 16)
            nn.BatchNorm2d(32),
            nn.LeakyReLU(0.2, inplace=True)
        )
        self.deconv3 = nn.Sequential(
            nn.ConvTranspose2d(32, 16, kernel_size=4, stride=2, padding=1),  # (B, 16, 32, 32)
            nn.BatchNorm2d(16),
            nn.LeakyReLU(0.2, inplace=True)
        )
        self.deconv4 = nn.Sequential(
            nn.ConvTranspose2d(16, 1, kernel_size=4, stride=2, padding=1),   # (B, 1, 64, 64)
            nn.Sigmoid()  # Bound pixel intensities strictly to [0.0, 1.0]
        )

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        z: (B, latent_dim)
        returns: (B, 1, 64, 64) in [0.0, 1.0]
        """
        x = self.fc_expand(z)
        x = x.view(-1, 64, 4, 4)
        x = self.deconv1(x)
        x = self.deconv2(x)
        x = self.deconv3(x)
        reconstruction = self.deconv4(x)
        return reconstruction
