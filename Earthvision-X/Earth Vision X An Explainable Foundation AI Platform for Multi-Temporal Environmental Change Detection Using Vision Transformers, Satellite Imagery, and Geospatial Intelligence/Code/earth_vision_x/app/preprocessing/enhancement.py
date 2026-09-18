"""
Image Enhancement and Noise Removal Module.
Applies CLAHE histogram equalization, Gaussian denoising, and contrast adjustments.
"""

import numpy as np
import cv2

class ImageEnhancer:
    @staticmethod
    def apply_clahe(image_rgb: np.ndarray, clip_limit: float = 2.0, tile_grid_size: int = 8) -> np.ndarray:
        """
        Applies Contrast Limited Adaptive Histogram Equalization (CLAHE) on the LAB L-channel.
        """
        img_uint = (image_rgb * 255).astype(np.uint8) if image_rgb.max() <= 1.0 else image_rgb.astype(np.uint8)
        lab = cv2.cvtColor(img_uint, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)

        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_grid_size, tile_grid_size))
        l_enhanced = clahe.apply(l)

        lab_enhanced = cv2.merge((l_enhanced, a, b))
        rgb_enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2RGB)
        return rgb_enhanced.astype(np.float32) / 255.0

    @staticmethod
    def remove_noise(image_rgb: np.ndarray) -> np.ndarray:
        """
        Applies Gaussian Denoising to filter satellite imagery sensor noise.
        """
        img_uint = (image_rgb * 255).astype(np.uint8) if image_rgb.max() <= 1.0 else image_rgb.astype(np.uint8)
        denoised = cv2.GaussianBlur(img_uint, (3, 3), 0)
        return denoised.astype(np.float32) / 255.0
