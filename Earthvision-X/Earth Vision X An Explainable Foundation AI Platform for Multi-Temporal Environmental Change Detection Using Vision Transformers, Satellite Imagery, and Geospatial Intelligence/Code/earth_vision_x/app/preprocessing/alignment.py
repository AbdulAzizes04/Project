"""
Image Co-registration and Spatial Alignment Module.
Aligns Image Time-2 to Image Time-1 using ORB keypoint feature matching and ECC transformation matrix.
"""

import numpy as np
import cv2
from typing import Tuple
from earth_vision_x.app.config.logging_config import logger

class ImageAligner:
    @staticmethod
    def align_pair(img_t1: np.ndarray, img_t2: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Aligns img_t2 to match spatial frame of img_t1.
        Returns: (aligned_t1, aligned_t2, alignment_score)
        """
        # Convert inputs to uint8 for OpenCV feature detection if needed
        t1_uint = (img_t1 * 255).astype(np.uint8) if img_t1.max() <= 1.0 else img_t1.astype(np.uint8)
        t2_uint = (img_t2 * 255).astype(np.uint8) if img_t2.max() <= 1.0 else img_t2.astype(np.uint8)

        t1_gray = cv2.cvtColor(t1_uint, cv2.COLOR_RGB2GRAY)
        t2_gray = cv2.cvtColor(t2_uint, cv2.COLOR_RGB2GRAY)

        # Detect ORB features
        orb = cv2.ORB_create(500)
        kp1, des1 = orb.detectAndCompute(t1_gray, None)
        kp2, des2 = orb.detectAndCompute(t2_gray, None)

        if des1 is None or des2 is None or len(kp1) < 4 or len(kp2) < 4:
            logger.warning("Not enough ORB keypoints found for image co-registration. Returning original pair.")
            return img_t1, img_t2, 1.0

        # Match keypoints
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        matches = sorted(matches, key=lambda x: x.distance)

        if len(matches) < 4:
            return img_t1, img_t2, 1.0

        src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

        # Compute Homography
        M, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
        if M is None:
            return img_t1, img_t2, 1.0

        h, w = t1_gray.shape
        aligned_t2 = cv2.warpPerspective(img_t2, M, (w, h))
        alignment_score = float(np.sum(mask) / len(matches)) if len(matches) > 0 else 0.0

        return img_t1, aligned_t2, alignment_score
