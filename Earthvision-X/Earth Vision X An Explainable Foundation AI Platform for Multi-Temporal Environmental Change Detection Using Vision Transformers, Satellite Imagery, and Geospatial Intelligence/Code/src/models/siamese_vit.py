"""
Siamese Vision Transformer (Siamese ViT) for Environmental Change Detection.
Features:
1. Weight-sharing Vision Transformer backbone (ViT-Base)
2. Retains self-attention matrices across all 12 transformer encoder blocks for Attention Rollout
3. Bitemporal difference fusion [F1, F2, |F1 - F2|]
4. Dual output heads: Binary change segmentation + Multi-class environmental classification
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Dict, Any, List, Optional
from torchvision.models import vit_b_16, ViT_B_16_Weights

from src.utils.logger import logger
from src.models.heads import BitemporalFeatureFusion, ChangeSegmentationHead, ChangeClassificationHead

class SiameseVisionTransformer(nn.Module):
    """
    Proposed Siamese Vision Transformer (Siamese-ViT) for Bitemporal Change Detection.
    """

    def __init__(
        self,
        in_channels: int = 3,
        num_segmentation_classes: int = 2,
        num_classification_classes: int = 5,
        pretrained: bool = False
    ):
        super().__init__()
        self.num_segmentation_classes = num_segmentation_classes
        self.num_classification_classes = num_classification_classes

        # Shared ViT-B/16 Backbone
        try:
            weights = ViT_B_16_Weights.DEFAULT if pretrained else None
            vit = vit_b_16(weights=weights)
        except Exception as e:
            logger.info(f"Initializing ViT-B/16 without remote weights: {e}")
            vit = vit_b_16(weights=None)

        self.patch_size = 16
        self.hidden_dim = 768
        self.patch_embedding = vit.conv_proj
        self.encoder_layers = vit.encoder.layers
        self.ln = vit.encoder.ln

        # Fusion block
        self.fusion = BitemporalFeatureFusion(in_channels=self.hidden_dim, out_channels=256)

        # Output heads
        self.seg_head = ChangeSegmentationHead(in_channels=256, num_classes=num_segmentation_classes)
        self.cls_head = ChangeClassificationHead(in_channels=256, num_classes=num_classification_classes)

        # Container for storing attention matrices during forward pass
        self.last_attention_matrices: List[torch.Tensor] = []

    def extract_features_and_attention(self, x: torch.Tensor) -> Tuple[torch.Tensor, List[torch.Tensor]]:
        """
        Extracts patch embeddings, passes through encoder layers, and records self-attention maps.
        Input: (B, C, H, W)
        Output: 2D Feature Map (B, hidden_dim, H/16, W/16), List of attention weights.
        """
        B, C, H, W = x.shape
        x_emb = self.patch_embedding(x) # (B, 768, H/16, W/16)
        H_feat, W_feat = x_emb.shape[2], x_emb.shape[3]

        tokens = x_emb.flatten(2).transpose(1, 2) # (B, N, 768)
        attentions = []

        for layer in self.encoder_layers:
            # Self-attention with weight recording
            norm_tokens = layer.ln_1(tokens)
            # Multihead attention
            attn_out, attn_weights = layer.self_attention(
                norm_tokens, norm_tokens, norm_tokens,
                need_weights=True,
                average_attn_weights=True
            )
            tokens = tokens + layer.dropout(attn_out)
            tokens = tokens + layer.mlp(layer.ln_2(tokens))
            if attn_weights is not None:
                attentions.append(attn_weights.detach())

        tokens = self.ln(tokens)
        feat_2d = tokens.transpose(1, 2).view(B, self.hidden_dim, H_feat, W_feat)
        return feat_2d, attentions

    def forward(
        self,
        t1: torch.Tensor,
        t2: torch.Tensor
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass for bitemporal satellite pair.
        Returns dictionary containing:
        - "seg_logits": (B, 2, H, W)
        - "cls_logits": (B, num_classes)
        - "fused_features": (B, 256, H/16, W/16)
        - "diff_features": (B, hidden_dim, H/16, W/16)
        """
        f1, att1 = self.extract_features_and_attention(t1)
        f2, att2 = self.extract_features_and_attention(t2)

        self.last_attention_matrices = att2 # T2 attention for explanation

        fused, diff = self.fusion(f1, f2)

        seg_logits = self.seg_head(fused)
        cls_logits = self.cls_head(fused)

        return {
            "seg_logits": seg_logits,
            "cls_logits": cls_logits,
            "fused_features": fused,
            "diff_features": diff
        }

    def get_attention_matrices(self) -> List[torch.Tensor]:
        """Returns the recorded transformer attention weights from the latest forward pass."""
        return self.last_attention_matrices
