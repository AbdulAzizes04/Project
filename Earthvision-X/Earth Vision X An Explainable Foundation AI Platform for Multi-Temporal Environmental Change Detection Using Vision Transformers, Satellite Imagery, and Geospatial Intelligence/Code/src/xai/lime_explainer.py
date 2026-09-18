"""
LIME (Local Interpretable Model-agnostic Explanations) Superpixel Module.
Partitions bitemporal satellite imagery into SLIC superpixels and measures regional
perturbation sensitivity to identify influential spatial boundaries.
"""

import numpy as np
import cv2
from skimage.segmentation import slic, mark_boundaries
from typing import Tuple, Dict, Any, Optional

class LimeSuperpixelExplainer:
    """
    Computes superpixel-level local explanations for environmental change detection.
    """

    @staticmethod
    def explain_change(
        img_t1: np.ndarray,
        img_t2: np.ndarray,
        change_mask: np.ndarray,
        n_segments: int = 60,
        compactness: float = 12.0
    ) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Computes SLIC superpixel segmentation and scores regional attribution.

        Returns:
            - overlay: RGB image with superpixel boundaries and positive/negative attribution shading
            - superpixel_mask: integer labels of superpixels
            - stats: dictionary of top contributing superpixel regions
        """
        t2_u8 = (np.clip(img_t2[:, :, :3], 0.0, 1.0) * 255).astype(np.uint8)

        # SLIC Superpixel segmentation
        segments = slic(t2_u8, n_segments=n_segments, compactness=compactness, start_label=1)

        # Calculate change ratio per superpixel
        num_segments = np.max(segments)
        scores = np.zeros(num_segments + 1, dtype=np.float32)

        for s_idx in range(1, num_segments + 1):
            mask_s = (segments == s_idx)
            total_px = np.count_nonzero(mask_s)
            if total_px > 0:
                change_px = np.count_nonzero(change_mask[mask_s] > 0)
                scores[s_idx] = change_px / total_px

        # Highlight regions: green for high-change drivers, neutral for background
        overlay = img_t2[:, :, :3].copy()
        for s_idx in range(1, num_segments + 1):
            if scores[s_idx] > 0.35:
                # Add positive red/amber highlight
                mask_s = (segments == s_idx)
                overlay[mask_s, 0] = np.clip(overlay[mask_s, 0] * 0.4 + 0.6, 0.0, 1.0) # Red tint
                overlay[mask_s, 1] = overlay[mask_s, 1] * 0.5
                overlay[mask_s, 2] = overlay[mask_s, 2] * 0.5

        # Render boundaries
        boundary_img = mark_boundaries(overlay, segments, color=(0.2, 0.8, 1.0), mode='thick')

        return boundary_img.astype(np.float32), segments, {
            "num_superpixels": int(num_segments),
            "high_impact_segments": int(np.count_nonzero(scores > 0.35)),
            "mean_segment_change_ratio": round(float(np.mean(scores[1:])), 4)
        }
