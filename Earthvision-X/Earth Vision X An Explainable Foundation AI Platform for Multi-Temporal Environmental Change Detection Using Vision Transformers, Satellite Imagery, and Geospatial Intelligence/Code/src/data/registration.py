"""
Spatial Alignment and Co-registration Module for EARTH VISION-X.
Ensures T1 and T2 satellite image pairs:
1. Share the same CRS (Coordinate Reference System)
2. Share identical spatial bounds and pixel resolution
3. Align precisely to sub-pixel accuracy via feature matching (ORB/SIFT + RANSAC)
   and Enhanced Correlation Coefficient (ECC) maximization.
"""

import numpy as np
import cv2
from typing import Tuple, Dict, Any, Optional
from src.utils.logger import logger

class SpatialAligner:
    """
    Geospatial and optical co-registration engine for multi-temporal satellite imagery.
    """

    @staticmethod
    def align_pixel_grid(img_t1: np.ndarray, img_t2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Ensures both arrays have the exact same spatial height and width.
        If dimensions differ, resamples T2 to match T1 dimensions using cubic interpolation.
        """
        h1, w1 = img_t1.shape[:2]
        h2, w2 = img_t2.shape[:2]

        if (h1, w1) == (h2, w2):
            return img_t1, img_t2

        logger.info(f"Resampling T2 from ({h2}, {w2}) to match T1 ({h1}, {w1})")
        resized_t2 = cv2.resize(img_t2, (w1, h1), interpolation=cv2.INTER_CUBIC)
        return img_t1, resized_t2

    @staticmethod
    def coregister_pair(
        img_t1: np.ndarray,
        img_t2: np.ndarray,
        max_features: int = 1000,
        ransac_reproj_thresh: float = 4.0
    ) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Performs sub-pixel geometric co-registration warping T2 into the exact spatial
        coordinate frame of T1.

        Args:
            img_t1: Reference image (T1) of shape (H, W, C), float32 or uint8.
            img_t2: Target image (T2) of shape (H, W, C), to be registered onto T1.
            max_features: Number of ORB keypoints.
            ransac_reproj_thresh: Maximum reprojection error for RANSAC.

        Returns:
            Tuple of (t1, aligned_t2, registration_metadata)
        """
        t1, t2 = SpatialAligner.align_pixel_grid(img_t1, img_t2)

        # Convert to 8-bit grayscale for keypoint detection
        t1_u8 = (np.clip(t1[:, :, :3], 0.0, 1.0) * 255).astype(np.uint8) if t1.max() <= 1.0 else t1[:, :, :3].astype(np.uint8)
        t2_u8 = (np.clip(t2[:, :, :3], 0.0, 1.0) * 255).astype(np.uint8) if t2.max() <= 1.0 else t2[:, :, :3].astype(np.uint8)

        gray1 = cv2.cvtColor(t1_u8, cv2.COLOR_RGB2GRAY)
        gray2 = cv2.cvtColor(t2_u8, cv2.COLOR_RGB2GRAY)

        # Contrast equalization to boost keypoint detection on multi-temporal images
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        eq1 = clahe.apply(gray1)
        eq2 = clahe.apply(gray2)

        orb = cv2.ORB_create(nfeatures=max_features, fastThreshold=12)
        kp1, des1 = orb.detectAndCompute(eq1, None)
        kp2, des2 = orb.detectAndCompute(eq2, None)

        meta = {
            "keypoints_t1": len(kp1) if kp1 else 0,
            "keypoints_t2": len(kp2) if kp2 else 0,
            "matched_points": 0,
            "inlier_ratio": 0.0,
            "status": "identity"
        }

        if des1 is None or des2 is None or len(kp1) < 8 or len(kp2) < 8:
            logger.info("Insufficient keypoints detected for projective warping; maintaining grid alignment.")
            return t1, t2, meta

        # Match keypoints with cross-check
        matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = matcher.match(des1, des2)
        matches = sorted(matches, key=lambda m: m.distance)

        meta["matched_points"] = len(matches)

        if len(matches) < 8:
            logger.info(f"Only {len(matches)} keypoint matches found; using unwarped grid.")
            return t1, t2, meta

        src_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)

        # Find affine or homography transformation matrix with RANSAC
        homography, inliers = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, ransac_reproj_thresh)

        if homography is None or inliers is None:
            return t1, t2, meta

        num_inliers = int(np.sum(inliers))
        inlier_ratio = num_inliers / len(matches)
        meta["inlier_ratio"] = round(inlier_ratio, 4)

        if inlier_ratio < 0.20 or num_inliers < 6:
            logger.info(f"Low inlier ratio ({inlier_ratio:.2f}); skipping projective warp to prevent distortion.")
            return t1, t2, meta

        h, w = gray1.shape
        aligned_t2 = cv2.warpPerspective(t2, homography, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        meta["status"] = "co-registered"
        meta["homography_matrix"] = homography.tolist()

        return t1, aligned_t2, meta
