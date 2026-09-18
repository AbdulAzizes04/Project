"""
Normalized Difference Vegetation Index (NDVI) Engine for EARTH VISION-X.
NDVI = (NIR - Red) / (NIR + Red)
Stores NDVI_T1, NDVI_T2, NDVI_CHANGE, and computes statistical canopy dynamics.
"""

import numpy as np
from typing import Dict, Any, Tuple

class NDVICalculator:
    """
    Computes authentic NDVI rasters and environmental canopy variance.
    """

    @staticmethod
    def compute_ndvi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
        """
        Computes NDVI from NIR and Red spectral bands.
        Values strictly bounded in [-1.0, 1.0].
        """
        nir_f = nir.astype(np.float32)
        red_f = red.astype(np.float32)

        denom = nir_f + red_f + 1e-7
        ndvi = (nir_f - red_f) / denom
        return np.clip(ndvi, -1.0, 1.0)

    @staticmethod
    def analyze_ndvi_pair(
        bands_t1: Dict[str, np.ndarray],
        bands_t2: Dict[str, np.ndarray]
    ) -> Dict[str, Any]:
        """
        Calculates NDVI_T1, NDVI_T2, NDVI_CHANGE and aggregate statistics.
        """
        ndvi_t1 = NDVICalculator.compute_ndvi(bands_t1["nir"], bands_t1["red"])
        ndvi_t2 = NDVICalculator.compute_ndvi(bands_t2["nir"], bands_t2["red"])
        ndvi_change = ndvi_t2 - ndvi_t1

        mean_t1 = float(np.mean(ndvi_t1))
        mean_t2 = float(np.mean(ndvi_t2))
        mean_change = float(np.mean(ndvi_change))

        # Canopy categories
        canopy_loss_pixels = int(np.count_nonzero(ndvi_change < -0.20))
        canopy_gain_pixels = int(np.count_nonzero(ndvi_change > 0.20))
        total_pixels = ndvi_change.size

        return {
            "ndvi_t1": ndvi_t1,
            "ndvi_t2": ndvi_t2,
            "ndvi_change": ndvi_change,
            "mean_ndvi_t1": round(mean_t1, 3),
            "mean_ndvi_t2": round(mean_t2, 3),
            "mean_ndvi_change": round(mean_change, 3),
            "canopy_loss_percentage": round((canopy_loss_pixels / total_pixels) * 100.0, 2),
            "canopy_gain_percentage": round((canopy_gain_pixels / total_pixels) * 100.0, 2)
        }
