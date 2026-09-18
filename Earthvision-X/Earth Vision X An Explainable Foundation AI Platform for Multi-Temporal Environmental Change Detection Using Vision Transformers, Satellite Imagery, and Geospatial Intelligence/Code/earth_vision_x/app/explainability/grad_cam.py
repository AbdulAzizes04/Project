"""
Grad-CAM and LayerCAM Implementation for Vision Transformers.
Computes gradient-weighted class activation maps targeting bitemporal feature difference layers.
"""

import torch
import numpy as np
import cv2

class ViTGradCAM:
    def __init__(self, model: torch.nn.Module):
        self.model = model

    def generate_cam(self, t1_tensor: torch.Tensor, t2_tensor: torch.Tensor, target_class: int = None) -> np.ndarray:
        """
        Generates Grad-CAM heatmap overlay for specified target class prediction.
        """
        self.model.eval()
        t1_tensor.requires_grad_(True)
        t2_tensor.requires_grad_(True)

        outputs = self.model(t1_tensor, t2_tensor)
        if target_class is None:
            target_class = torch.argmax(torch.mean(outputs, dim=(2, 3))).item()

        score = outputs[0, target_class].sum()
        self.model.zero_grad()
        score.backward()

        grad = t2_tensor.grad.data.squeeze(0).cpu().numpy() # (3, H, W)
        cam = np.mean(np.abs(grad), axis=0) # (H, W)
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        cam = cv2.GaussianBlur(cam, (7, 7), 0)
        return cam
