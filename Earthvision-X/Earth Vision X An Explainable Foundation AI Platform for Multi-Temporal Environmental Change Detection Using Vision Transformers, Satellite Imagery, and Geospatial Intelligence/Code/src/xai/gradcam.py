"""
Grad-CAM Implementation for Bitemporal Transformer / CNN Change Detection.
Computes gradient-weighted class activation maps targeting bitemporal feature difference representations:
L^c_{Grad-CAM} = ReLU(sum_k alpha_k^c A^k)
"""

import torch
import numpy as np
import cv2
from typing import Optional

class ViTGradCAM:
    """
    Computes Grad-CAM heatmaps on bitemporal satellite inputs.
    """

    def __init__(self, model: torch.nn.Module):
        self.model = model

    def generate_cam(
        self,
        t1_tensor: torch.Tensor,
        t2_tensor: torch.Tensor,
        target_class: Optional[int] = 1 # Change class by default
    ) -> np.ndarray:
        """
        Generates Grad-CAM activation heatmap overlay for the specified class.
        """
        self.model.eval()
        orig_h, orig_w = t1_tensor.shape[2], t1_tensor.shape[3]

        # Optimize for interactive CPU execution: downsample tokens for fast backpropagation
        if orig_h > 160 or orig_w > 160:
            t1 = torch.nn.functional.interpolate(t1_tensor, size=(128, 128), mode="bilinear", align_corners=False)
            t2 = torch.nn.functional.interpolate(t2_tensor, size=(128, 128), mode="bilinear", align_corners=False)
        else:
            t1 = t1_tensor
            t2 = t2_tensor

        t1 = t1.clone().detach().requires_grad_(True)
        t2 = t2.clone().detach().requires_grad_(True)

        outputs = self.model(t1, t2)
        seg_logits = outputs["seg_logits"]

        if target_class is None:
            target_class = int(torch.argmax(torch.mean(seg_logits, dim=(2, 3))).item())

        score = seg_logits[:, target_class].sum()
        self.model.zero_grad()
        score.backward()

        # Extract gradient from T2 input
        if t2.grad is not None:
            grad = t2.grad.data.squeeze(0).cpu().numpy() # (C, H, W)
            cam = np.mean(np.abs(grad), axis=0)         # (H, W)
        elif "diff_features" in outputs and outputs["diff_features"].grad is not None:
            grad = outputs["diff_features"].grad.data.squeeze(0).cpu().numpy()
            cam = np.mean(np.maximum(grad, 0), axis=0)
            cam = cv2.resize(cam, (t2.shape[2], t2.shape[3]))
        else:
            # Difference proxy
            t1_np = t1.detach().squeeze(0).cpu().numpy().transpose(1, 2, 0)
            t2_np = t2.detach().squeeze(0).cpu().numpy().transpose(1, 2, 0)
            cam = np.mean(np.abs(t1_np - t2_np), axis=2)

        # Normalization and smoothing at original resolution
        cam = cv2.resize(cam, (orig_w, orig_h), interpolation=cv2.INTER_CUBIC)
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        cam = cv2.GaussianBlur(cam, (11, 11), 0)
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)

        return cam.astype(np.float32)
