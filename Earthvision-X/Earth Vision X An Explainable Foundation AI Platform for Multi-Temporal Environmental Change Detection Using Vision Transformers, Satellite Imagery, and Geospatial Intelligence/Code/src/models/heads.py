"""
Feature Fusion and Multi-Task Output Heads for EARTH VISION-X.
Implements:
1. Feature Fusion Block: D = |F_T1 - F_T2|, Concat [F_T1, F_T2, D]
2. Head 1 - Change Segmentation Head: Pixel-level binary change mask (Changed vs Unchanged)
3. Head 2 - Change Classification Head: Multi-class environmental change category logits
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Dict

class ConvBlock(nn.Module):
    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.conv(x)

class BitemporalFeatureFusion(nn.Module):
    """
    Computes difference embedding D = |F_T1 - F_T2|
    and concatenates [F_T1, F_T2, D] into a unified representation.
    """
    def __init__(self, in_channels: int = 768, out_channels: int = 256):
        super().__init__()
        self.proj = nn.Sequential(
            nn.Conv2d(in_channels * 3, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Dropout2d(0.1)
        )

    def forward(self, f1: torch.Tensor, f2: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        diff = torch.abs(f1 - f2)
        fused = torch.cat([f1, f2, diff], dim=1) # (B, 3*C, H, W)
        out = self.proj(fused)                  # (B, out_channels, H, W)
        return out, diff

class ChangeSegmentationHead(nn.Module):
    """
    Decoder Head 1: Generates high-resolution binary change segmentation mask.
    Outputs logits: (B, 2, H, W) -> [Background/Unchanged, Changed].
    """
    def __init__(self, in_channels: int = 256, num_classes: int = 2):
        super().__init__()
        self.up1 = nn.ConvTranspose2d(in_channels, 128, kernel_size=4, stride=2, padding=1)
        self.dec1 = ConvBlock(128, 128)

        self.up2 = nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1)
        self.dec2 = ConvBlock(64, 64)

        self.up3 = nn.ConvTranspose2d(64, 32, kernel_size=4, stride=2, padding=1)
        self.dec3 = ConvBlock(32, 32)

        self.up4 = nn.ConvTranspose2d(32, 16, kernel_size=4, stride=2, padding=1)
        self.dec4 = ConvBlock(16, 16)

        self.classifier = nn.Conv2d(16, num_classes, kernel_size=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.dec1(self.up1(x))
        x = self.dec2(self.up2(x))
        x = self.dec3(self.up3(x))
        x = self.dec4(self.up4(x))
        logits = self.classifier(x)
        return logits

class ChangeClassificationHead(nn.Module):
    """
    Head 2: Multi-class environmental change classifier.
    Exposes category logits over trained classes (e.g. Deforestation, Urban Sprawl, Water Body Change).
    """
    def __init__(self, in_channels: int = 256, num_classes: int = 5):
        super().__init__()
        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(in_channels, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(128, num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        pooled = self.pool(x)
        logits = self.fc(pooled)
        return logits
