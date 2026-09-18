"""
Siamese ResNet/CNN Baseline Model for Bitemporal Change Detection.
Employs shared convolutional weights and difference feature fusion.
"""

import torch
import torch.nn as nn
from torchvision.models import resnet18, ResNet18_Weights
from typing import Dict
from src.models.heads import BitemporalFeatureFusion, ChangeSegmentationHead, ChangeClassificationHead

class SiameseCNNChangeDetector(nn.Module):
    """
    Standard Siamese CNN (ResNet-18) baseline for bitemporal satellite change detection.
    """

    def __init__(self, in_channels: int = 3, num_classes: int = 2):
        super().__init__()
        try:
            res = resnet18(weights=ResNet18_Weights.DEFAULT)
        except Exception:
            res = resnet18(weights=None)

        self.conv1 = res.conv1
        self.bn1 = res.bn1
        self.relu = res.relu
        self.maxpool = res.maxpool

        self.layer1 = res.layer1 # 64
        self.layer2 = res.layer2 # 128
        self.layer3 = res.layer3 # 256
        self.layer4 = res.layer4 # 512

        self.fusion = BitemporalFeatureFusion(in_channels=512, out_channels=256)
        self.seg_head = ChangeSegmentationHead(in_channels=256, num_classes=num_classes)
        self.cls_head = ChangeClassificationHead(in_channels=256, num_classes=5)

    def extract_features(self, x: torch.Tensor) -> torch.Tensor:
        x = self.relu(self.bn1(self.conv1(x)))
        x = self.maxpool(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x) # (B, 512, H/32, W/32)
        return x

    def forward(self, t1: torch.Tensor, t2: torch.Tensor) -> Dict[str, torch.Tensor]:
        f1 = self.extract_features(t1)
        f2 = self.extract_features(t2)

        fused, diff = self.fusion(f1, f2)
        seg_logits = self.seg_head(fused)
        if seg_logits.shape[2:] != t1.shape[2:]:
            seg_logits = torch.nn.functional.interpolate(seg_logits, size=t1.shape[2:], mode="bilinear", align_corners=False)
        cls_logits = self.cls_head(fused)

        return {
            "seg_logits": seg_logits,
            "cls_logits": cls_logits,
            "fused_features": fused,
            "diff_features": diff
        }
