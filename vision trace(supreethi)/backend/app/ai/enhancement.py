import cv2
import numpy as np
from typing import Tuple

class LowLightEnhancer:
    """
    Forensic Low-Light & Surveillance Video Frame Enhancer.
    Techniques:
    - LAB Color Space CLAHE (Contrast Limited Adaptive Histogram Equalization)
    - Non-linear Gamma Expansion (illuminates deep shadows without blowing highlights)
    - Edge-preserving Bilateral Filter (suppresses camera sensor ISO noise)
    - Detail Unsharp Masking
    """
    def __init__(self, clip_limit: float = 3.0, tile_grid_size: Tuple[int, int] = (8, 8)):
        self.clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)

    def enhance_frame(self, frame: np.ndarray, gamma: float = 1.45, apply_denoise: bool = True) -> np.ndarray:
        if frame is None or frame.size == 0:
            return frame

        # Step 1: Gamma correction to lift dark shadow details
        inv_gamma = 1.0 / max(0.1, gamma)
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        gamma_corrected = cv2.LUT(frame, table)

        # Step 2: Convert to LAB color space and apply CLAHE to L channel only (preserves color balance)
        lab = cv2.cvtColor(gamma_corrected, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        enhanced_l = self.clahe.apply(l_channel)
        enhanced_lab = cv2.merge((enhanced_l, a_channel, b_channel))
        enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

        # Step 3: Edge-preserving noise reduction
        if apply_denoise:
            denoised = cv2.bilateralFilter(enhanced_bgr, d=5, sigmaColor=35, sigmaSpace=35)
        else:
            denoised = enhanced_bgr

        # Step 4: Subtle unsharp mask to restore forensic sharpness
        gaussian = cv2.GaussianBlur(denoised, (0, 0), 2.0)
        sharpened = cv2.addWeighted(denoised, 1.25, gaussian, -0.25, 0)

        return sharpened

    def create_side_by_side_comparison(self, original: np.ndarray, enhanced: np.ndarray) -> np.ndarray:
        """Combines original and enhanced frames with a forensic split indicator."""
        h, w = original.shape[:2]
        canvas = np.zeros((h, w, 3), dtype=np.uint8)
        split_x = w // 2

        canvas[:, :split_x] = original[:, :split_x]
        canvas[:, split_x:] = enhanced[:, split_x:]

        # Draw dividing neon cyan line
        cv2.line(canvas, (split_x, 0), (split_x, h), (255, 230, 0), 2)
        # Add labels
        cv2.putText(canvas, "ORIGINAL RAW CCTV", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200, 200, 200), 2)
        cv2.putText(canvas, "VISIONTRACE CLAHE ENHANCED", (split_x + 20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 230, 0), 2)

        return canvas
