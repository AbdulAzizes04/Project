"""
Bitemporal U-Net Baseline Model for Environmental Change Detection.
Processes concatenated (T1, T2) satellite rasters via an encoder-decoder architecture with skip connections.
"""

import torch
import torch.nn as nn
from typing import Dict
from src.models.heads import ConvBlock

class UNetChangeDetector(nn.Module):
    """
    Standard U-Net baseline architecture for bitemporal change detection.
    """

    def __init__(self, in_channels: int = 6, num_classes: int = 2):
        super().__init__()
        # Encoder
        self.enc1 = ConvBlock(in_channels, 64)
        self.pool1 = nn.MaxPool2d(2)

        self.enc2 = ConvBlock(64, 128)
        self.pool2 = nn.MaxPool2d(2)

        self.enc3 = ConvBlock(128, 256)
        self.pool3 = nn.MaxPool2d(2)

        self.enc4 = ConvBlock(256, 512)
        self.pool4 = nn.MaxPool2d(2)

        # Bottleneck
        self.bottleneck = ConvBlock(512, 1024)

        # Decoder
        self.up4 = nn.ConvTranspose2d(1024, 512, kernel_size=2, stride=2)
        self.dec4 = ConvBlock(1024, 512)

        self.up3 = nn.ConvTranspose2d(512, 256, kernel_size=2, stride=2)
        self.dec3 = ConvBlock(512, 256)

        self.up2 = nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2)
        self.dec2 = ConvBlock(256, 128)

        self.up1 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
        self.dec1 = ConvBlock(128, 64)

        self.classifier = nn.Conv2d(64, num_classes, kernel_size=1)
        self.cls_head = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(1024, 5)
        )

    def forward(self, t1: torch.Tensor, t2: torch.Tensor) -> Dict[str, torch.Tensor]:
        x = torch.cat([t1, t2], dim=1) # (B, 6, H, W)

        e1 = self.enc1(x)
        e2 = self.enc2(self.pool1(e1))
        e3 = self.enc3(self.pool2(e2))
        e4 = self.enc4(self.pool3(e3))

        b = self.bottleneck(self.pool4(e4))

        d4 = self.dec4(torch.cat([self.up4(b), e4], dim=1))
        d3 = self.dec3(torch.cat([self.up3(d4), e3], dim=1))
        d2 = self.dec2(torch.cat([self.up2(d3), e2], dim=1))
        d1 = self.dec1(torch.cat([self.up1(d2), e1], dim=1))

        seg_logits = self.classifier(d1)
        cls_logits = self.cls_head(b)

        return {
            "seg_logits": seg_logits,
            "cls_logits": cls_logits,
            "fused_features": b
        }
