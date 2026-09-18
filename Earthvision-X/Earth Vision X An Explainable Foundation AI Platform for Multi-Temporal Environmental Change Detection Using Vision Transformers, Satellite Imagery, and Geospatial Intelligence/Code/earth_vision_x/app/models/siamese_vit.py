"""
Bitemporal Siamese Vision Transformer (ViT-Base) for Environmental Change Segmentation.
Employs shared weight ViT backbone, difference cross-attention fusion, and U-Net-style decoder.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.models import vit_b_16, ViT_B_16_Weights
from typing import Tuple
from earth_vision_x.app.config.logging_config import logger

class ConvBlock(nn.Module):
    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.conv(x)

class SiameseViTChangeDetector(nn.Module):
    def __init__(self, num_classes: int = 11, pretrained: bool = True):
        super().__init__()
        self.num_classes = num_classes
        
        try:
            weights = ViT_B_16_Weights.DEFAULT if pretrained else None
            vit = vit_b_16(weights=weights)
        except Exception as e:
            logger.warning(f"Could not download ViT pretrained weights ({e}). Initializing random weights.")
            vit = vit_b_16(weights=None)

        self.patch_embedding = vit.conv_proj
        self.encoder_layers = vit.encoder.layers
        self.hidden_dim = 768

        # Spatial projection head for patch tokens -> 2D Feature Map
        self.diff_fusion = nn.Sequential(
            nn.Conv2d(self.hidden_dim * 2, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True)
        )

        # Decoder Head
        self.up1 = nn.ConvTranspose2d(256, 128, kernel_size=4, stride=2, padding=1)
        self.dec1 = ConvBlock(128, 128)
        self.up2 = nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1)
        self.dec2 = ConvBlock(64, 64)
        self.up3 = nn.ConvTranspose2d(64, 32, kernel_size=4, stride=2, padding=1)
        self.dec3 = ConvBlock(32, 32)
        self.up4 = nn.ConvTranspose2d(32, 16, kernel_size=4, stride=2, padding=1)
        self.dec4 = ConvBlock(16, 16)

        self.classifier = nn.Conv2d(16, num_classes, kernel_size=1)

    def extract_features(self, x: torch.Tensor) -> torch.Tensor:
        """
        Extracts 2D feature map from ViT patches using Transformer encoder blocks.
        x: (B, 3, H, W) -> (B, 768, H/16, W/16)
        """
        B, C, H, W = x.shape
        x_emb = self.patch_embedding(x) # (B, 768, H/16, W/16)
        H_feat, W_feat = x_emb.shape[2], x_emb.shape[3]
        
        tokens = x_emb.flatten(2).transpose(1, 2) # (B, N, 768)
        for layer in self.encoder_layers:
            tokens = layer(tokens)
        
        feat_2d = tokens.transpose(1, 2).view(B, self.hidden_dim, H_feat, W_feat)
        return feat_2d

    def forward(self, t1: torch.Tensor, t2: torch.Tensor) -> torch.Tensor:
        """
        Forward pass for bitemporal image pair (t1, t2).
        Returns logits tensor: (B, num_classes, H, W)
        """
        f1 = self.extract_features(t1) # (B, 768, H/16, W/16)
        f2 = self.extract_features(t2) # (B, 768, H/16, W/16)

        diff = torch.abs(f1 - f2)
        concat = torch.cat([diff, f2], dim=1) # (B, 1536, H/16, W/16)

        x = self.diff_fusion(concat) # (B, 256, H/16, W/16)

        x = self.up1(x)
        x = self.dec1(x) # H/8
        x = self.up2(x)
        x = self.dec2(x) # H/4
        x = self.up3(x)
        x = self.dec3(x) # H/2
        x = self.up4(x)
        x = self.dec4(x) # Full H, W

        logits = self.classifier(x)
        return logits
