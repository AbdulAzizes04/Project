"""
Normalized Difference Water Index (NDWI) Engine for EARTH VISION-X.
NDWI = (Green - NIR) / (Green + NIR)
Stores NDWI_T1, NDWI_T2, NDWI_CHANGE, and computes hydrological surface variance.
"""

import numpy as np
from typing import Dict, Any, Tuple

class NDWICalculator:
    """
    Computes authentic NDWI rasters and water body boundary dynamics.
    """

    @staticmethod
    def compute_ndwi(green: np.ndarray, nir: np.ndarray) -> np.ndarray:
        """
        Computes McFeeters NDWI from Green and NIR bands.
        Values strictly bounded in [-1.0, 1.0]. Water bodies typically have NDWI > 0.
        """
        green_f = green.astype(np.float32)
        nir_f = nir.astype(np.float32)

        denom = green_f + nir_f + 1e-7
        ndwi = (green_f - nir_f) / denom
        return np.clip(ndwi, -1.0, 1.0)

    @staticmethod
    def analyze_ndwi_pair(
        bands_t1: Dict[str, np.ndarray],
        bands_t2: Dict[str, np.ndarray]
    ) -> Dict[str, Any]:
        """
        Calculates NDWI_T1, NDWI_T2, NDWI_CHANGE and hydrological statistics.
        """
        ndwi_t1 = NDWICalculator.compute_ndwi(bands_t1["green"], bands_t1["nir"])
        ndwi_t2 = NDWICalculator.compute_ndwi(bands_t2["green"], bands_t2["nir"])
        ndwi_change = ndwi_t2 - ndwi_t1

        mean_t1 = float(np.mean(ndwi_t1))
        mean_t2 = float(np.mean(ndwi_t2))
        mean_change = float(np.mean(ndwi_change))

        # Water threshold (typically NDWI > 0.0)
        water_t1_px = int(np.count_nonzero(ndwi_t1 > 0.0))
        water_t2_px = int(np.count_nonzero(ndwi_t2 > 0.0))
        total_pixels = ndwi_change.size

        return {
            "ndwi_t1": ndwi_t1,
            "ndwi_t2": ndwi_t2,
            "ndwi_change": ndwi_change,
            "mean_ndwi_t1": round(mean_t1, 3),
            "mean_ndwi_t2": round(mean_t2, 3),
            "mean_ndwi_change": round(mean_change, 3),
            "water_extent_t1_percentage": round((water_t1_px / total_pixels) * 100.0, 2),
            "water_extent_t2_percentage": round((water_t2_px / total_pixels) * 100.0, 2),
            "water_surface_delta_percentage": round(((water_t2_px - water_t1_px) / total_pixels) * 100.0, 2)
        }
