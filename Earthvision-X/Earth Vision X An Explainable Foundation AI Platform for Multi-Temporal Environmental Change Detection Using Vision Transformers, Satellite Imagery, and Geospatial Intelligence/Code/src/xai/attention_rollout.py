"""
Vision Transformer Attention Rollout Module for EARTH VISION-X.
Recursively computes attention rollout across multi-head self-attention matrices:
R_0 = I
R_{l} = (0.5 * A_l + 0.5 * I) * R_{l-1}
Traces information propagation from patch tokens to environmental change boundaries.
"""

import numpy as np
import torch
import cv2
from typing import List, Optional
from src.utils.logger import logger

class AttentionRollout:
    """
    Computes true attention rollout for Vision Transformers.
    """

    @staticmethod
    def compute_rollout_from_matrices(
        attention_matrices: List[torch.Tensor],
        discard_ratio: float = 0.85,
        head_fusion: str = "mean"
    ) -> np.ndarray:
        """
        Computes attention rollout from a list of layer attention matrices.
        Each matrix has shape (B, N, N) or (B, num_heads, N, N).
        """
        if not attention_matrices:
            return np.ones((256, 256), dtype=np.float32)

        # Work on first item in batch
        rollout = None

        for attn in attention_matrices:
            if attn.ndim == 4: # (B, heads, N, N)
                if head_fusion == "mean":
                    a = torch.mean(attn[0], dim=0) # (N, N)
                elif head_fusion == "max":
                    a = torch.max(attn[0], dim=0)[0]
                else:
                    a = torch.min(attn[0], dim=0)[0]
            elif attn.ndim == 3: # (B, N, N)
                a = attn[0]
            else:
                continue

            # Add identity matrix to account for residual connections
            I = torch.eye(a.size(0), device=a.device)
            a = a + I
            a = a / torch.sum(a, dim=-1, keepdim=True)

            if rollout is None:
                rollout = a
            else:
                rollout = torch.matmul(a, rollout)

        if rollout is None:
            return np.ones((256, 256), dtype=np.float32)

        # Average token influence across patches
        mask = torch.mean(rollout, dim=0).cpu().numpy()

        # Reshape tokens into 2D spatial grid (e.g. 32x32 from 1024 tokens for 512x512 with patch 16)
        num_tokens = mask.shape[0]
        side = int(np.sqrt(num_tokens))
        if side * side == num_tokens:
            spatial_mask = mask.reshape(side, side)
        else:
            # Handle potential CLS token
            valid_side = int(np.sqrt(num_tokens - 1))
            if valid_side * valid_side == num_tokens - 1:
                spatial_mask = mask[1:].reshape(valid_side, valid_side)
            else:
                spatial_mask = cv2.resize(mask, (32, 32))

        # Normalize and resize to standard resolution
        norm = (spatial_mask - spatial_mask.min()) / (spatial_mask.max() - spatial_mask.min() + 1e-8)
        norm = cv2.resize(norm, (512, 512), interpolation=cv2.INTER_CUBIC)
        norm = cv2.GaussianBlur(norm, (9, 9), 0)
        norm = (norm - norm.min()) / (norm.max() - norm.min() + 1e-8)

        return norm.astype(np.float32)

    @staticmethod
    def compute_rollout_from_model(
        model: torch.nn.Module,
        t1_tensor: torch.Tensor,
        t2_tensor: torch.Tensor
    ) -> np.ndarray:
        """
        Runs forward pass on model and extracts recorded self-attention matrices.
        """
        model.eval()
        with torch.no_grad():
            outputs = model(t1_tensor, t2_tensor)
            if hasattr(model, "get_attention_matrices"):
                attn_mats = model.get_attention_matrices()
                if attn_mats:
                    return AttentionRollout.compute_rollout_from_matrices(attn_mats)

            # Fallback to feature gradient / difference attention proxy if raw matrices missing
            if "diff_features" in outputs:
                diff = outputs["diff_features"]
                att = torch.mean(diff, dim=1).squeeze(0).cpu().numpy()
                norm = (att - att.min()) / (att.max() - att.min() + 1e-8)
                return cv2.resize(norm, (512, 512), interpolation=cv2.INTER_CUBIC)

        return np.ones((512, 512), dtype=np.float32)
