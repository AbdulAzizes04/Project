"""
Satellite Change Map and Color Overlay Generator.
Visualizes categorical change masks, difference maps, and confidence overlays.
"""

import numpy as np
import cv2
import matplotlib.pyplot as plt
from typing import Tuple
from earth_vision_x.app.config.constants import CHANGE_COLOR_MAP, CHANGE_CLASSES

class ChangeMapVisualizer:
    @staticmethod
    def create_color_mask(change_mask: np.ndarray) -> np.ndarray:
        """
        Maps categorical change mask (H, W) to RGB color map.
        """
        H, W = change_mask.shape
        rgb_mask = np.zeros((H, W, 3), dtype=np.uint8)

        # Hex to RGB mapping
        for idx, name in enumerate(CHANGE_CLASSES):
            hex_color = CHANGE_COLOR_MAP.get(name, "#FFFFFF")
            rgb_val = [int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]
            rgb_mask[change_mask == idx] = rgb_val

        return rgb_mask

    @staticmethod
    def create_overlay(img_t2: np.ndarray, change_mask: np.ndarray, alpha: float = 0.5) -> np.ndarray:
        """
        Blends colored change mask onto Image Time-2.
        """
        t2_uint = (img_t2 * 255).astype(np.uint8) if img_t2.max() <= 1.0 else img_t2.astype(np.uint8)
        H, W = t2_uint.shape[:2]

        if change_mask.shape[:2] != (H, W):
            change_mask = cv2.resize(change_mask.astype(np.uint8), (W, H), interpolation=cv2.INTER_NEAREST)

        color_mask = ChangeMapVisualizer.create_color_mask(change_mask)
        overlay = cv2.addWeighted(t2_uint, 1.0 - alpha, color_mask, alpha, 0)
        return overlay

    @staticmethod
    def create_difference_map(img_t1: np.ndarray, img_t2: np.ndarray) -> np.ndarray:
        """
        Calculates pixel-wise absolute difference map across time-steps.
        """
        H, W = img_t1.shape[:2]
        if img_t2.shape[:2] != (H, W):
            img_t2 = cv2.resize(img_t2, (W, H))

        diff = np.abs(img_t1.astype(np.float32) - img_t2.astype(np.float32))
        diff_mag = np.mean(diff, axis=2) # (H, W)
        diff_norm = (diff_mag - diff_mag.min()) / (diff_mag.max() - diff_mag.min() + 1e-8)
        
        # Colorize using Jet colormap
        diff_uint = (diff_norm * 255).astype(np.uint8)
        heatmap = cv2.applyColorMap(diff_uint, cv2.COLORMAP_JET)
        heatmap_rgb = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
        return heatmap_rgb
