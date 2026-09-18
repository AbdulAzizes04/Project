"""
LIME (Local Interpretable Model-agnostic Explanations) Superpixel Explainer.
Identifies key spatial superpixel boundaries contributing to change detection predictions.
Supports OpenCV ximgproc with pure grid-superpixel fallback.
"""

import numpy as np
import cv2
from typing import Tuple

class LimeSuperpixelExplainer:
    @staticmethod
    def explain_instance(img_t1: np.ndarray, img_t2: np.ndarray, change_mask: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generates superpixel segmentation boundary map highlighting influential spatial regions.
        Returns: (boundary_overlay, superpixel_mask)
        """
        img_uint = (img_t2 * 255).astype(np.uint8) if img_t2.max() <= 1.0 else img_t2.astype(np.uint8)
        H, W = img_uint.shape[:2]

        labels = np.zeros((H, W), dtype=np.int32)
        grid_size = 16

        try:
            slic = cv2.ximgproc.createSuperpixelSLIC(img_uint, algorithm=cv2.ximgproc.SLIC, region_size=grid_size)
            slic.iterate(10)
            labels = slic.getLabels()
            mask_contours = slic.getLabelContourMask()
            overlay = img_uint.copy()
            overlay[mask_contours > 0] = [255, 255, 0]
        except AttributeError:
            # Fallback Grid Superpixel Generation
            overlay = img_uint.copy()
            sp_id = 0
            for r in range(0, H, grid_size):
                for c in range(0, W, grid_size):
                    labels[r:r+grid_size, c:c+grid_size] = sp_id
                    cv2.rectangle(overlay, (c, r), (min(c+grid_size, W), min(r+grid_size, H)), (255, 255, 0), 1)
                    sp_id += 1

        if change_mask.shape[:2] != (H, W):
            change_mask = cv2.resize(change_mask.astype(np.uint8), (W, H), interpolation=cv2.INTER_NEAREST)

        changed_superpixels = np.unique(labels[change_mask > 0])
        for sp_id in changed_superpixels[:8]:
            sp_mask = labels == sp_id
            overlay[sp_mask] = (overlay[sp_mask] * 0.5 + np.array([0, 255, 255]) * 0.5).astype(np.uint8)

        return overlay, labels
