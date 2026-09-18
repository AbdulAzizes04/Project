"""
Swin Transformer Bitemporal Architecture for Hierarchical Satellite Change Detection.
"""

import torch
import torch.nn as nn
from torchvision.models import swin_s, Swin_S_Weights

class SwinChangeDetector(nn.Module):
    def __init__(self, num_classes: int = 11, pretrained: bool = True):
        super().__init__()
        self.num_classes = num_classes

        # Backbone Swin Transformer
        weights = Swin_S_Weights.DEFAULT if pretrained else None
        swin = swin_s(weights=weights)
        self.features = swin.features

        # Swin-S features shape: (B, 768, H/32, W/32)
        self.fusion = nn.Sequential(
            nn.Conv2d(768 * 2, 384, 3, padding=1),
            nn.BatchNorm2d(384),
            nn.ReLU(True)
        )

        self.up_blocks = nn.Sequential(
            nn.ConvTranspose2d(384, 192, 4, stride=2, padding=1),
            nn.BatchNorm2d(192),
            nn.ReLU(True),
            nn.ConvTranspose2d(192, 96, 4, stride=2, padding=1),
            nn.BatchNorm2d(96),
            nn.ReLU(True),
            nn.ConvTranspose2d(96, 48, 4, stride=2, padding=1),
            nn.BatchNorm2d(48),
            nn.ReLU(True),
            nn.ConvTranspose2d(48, 24, 4, stride=2, padding=1),
            nn.BatchNorm2d(24),
            nn.ReLU(True),
            nn.ConvTranspose2d(24, 12, 4, stride=2, padding=1),
            nn.BatchNorm2d(12),
            nn.ReLU(True),
            nn.Conv2d(12, num_classes, 1)
        )

    def extract_features(self, x: torch.Tensor) -> torch.Tensor:
        feat = self.features(x) # (B, H/32, W/32, 768)
        if feat.ndim == 4 and feat.shape[-1] == 768:
            feat = feat.permute(0, 3, 1, 2).contiguous() # (B, 768, H/32, W/32)
        return feat

    def forward(self, t1: torch.Tensor, t2: torch.Tensor) -> torch.Tensor:
        f1 = self.extract_features(t1)
        f2 = self.extract_features(t2)

        diff = torch.abs(f1 - f2)
        cat = torch.cat([diff, f2], dim=1)
        fused = self.fusion(cat)
        logits = self.up_blocks(fused)
        return logits
