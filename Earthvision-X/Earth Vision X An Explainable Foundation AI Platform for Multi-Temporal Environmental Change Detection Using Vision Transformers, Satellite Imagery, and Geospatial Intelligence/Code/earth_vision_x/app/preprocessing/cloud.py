"""
Cloud Detection and Masking Module.
Identifies high-reflectance cloud regions and shadows, generating a cloud mask.
"""

import numpy as np
import cv2

class CloudMasker:
    @staticmethod
    def detect_clouds(image_rgb: np.ndarray, brightness_threshold: float = 0.82) -> np.ndarray:
        """
        Detects cloud presence based on luminance and color saturation heuristics.
        Returns a binary mask (H, W) where 1 indicates cloud cover.
        """
        # Convert RGB to HSV to check saturation and brightness
        img_uint = (image_rgb * 255).astype(np.uint8) if image_rgb.max() <= 1.0 else image_rgb.astype(np.uint8)
        hsv = cv2.cvtColor(img_uint, cv2.COLOR_RGB2HSV)

        value = hsv[:, :, 2] / 255.0  # Brightness
        saturation = hsv[:, :, 1] / 255.0 # Color saturation (clouds have very low saturation)

        # Cloud heuristic: high brightness + low saturation
        cloud_mask = (value > brightness_threshold) & (saturation < 0.25)
        return cloud_mask.astype(np.uint8)

    @staticmethod
    def mask_and_repair(image_rgb: np.ndarray, cloud_mask: np.ndarray) -> np.ndarray:
        """
        Applies cloud mask and performs OpenCV Telea inpainting for cloud removal.
        """
        img_uint = (image_rgb * 255).astype(np.uint8) if image_rgb.max() <= 1.0 else image_rgb.astype(np.uint8)
        mask_uint = cloud_mask.astype(np.uint8) * 255

        if np.count_nonzero(mask_uint) == 0:
            return image_rgb

        repaired = cv2.inpaint(img_uint, mask_uint, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
        return (repaired.astype(np.float32) / 255.0)
