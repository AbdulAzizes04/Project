"""
Radiometric Normalization, Band Stacking, and AOI Clipping for EARTH VISION-X.
"""

import numpy as np
import cv2
from typing import Tuple, Dict, Any, Optional
from src.utils.logger import logger

class SatellitePreprocessor:
    """
    Multispectral radiometric normalization, AOI cropping, and band tensor preparation.
    """

    @staticmethod
    def normalize_reflectance(
        raster: np.ndarray,
        method: str = "percentile",
        p_min: float = 2.0,
        p_max: float = 98.0
    ) -> np.ndarray:
        """
        Radiometric normalization across all spectral channels.
        Percentile clipping removes cloud glint and water absorb outliers.
        """
        arr = raster.astype(np.float32)

        if method == "percentile":
            out = np.zeros_like(arr)
            channels = arr.shape[2] if arr.ndim == 3 else 1
            if arr.ndim == 2:
                arr = arr[:, :, np.newaxis]
                out = out[:, :, np.newaxis]

            for c in range(arr.shape[2]):
                band = arr[:, :, c]
                valid = band[~np.isnan(band)]
                if valid.size == 0:
                    continue
                v_min = np.percentile(valid, p_min)
                v_max = np.percentile(valid, p_max)
                if v_max > v_min:
                    clipped = np.clip(band, v_min, v_max)
                    out[:, :, c] = (clipped - v_min) / (v_max - v_min)
                else:
                    out[:, :, c] = np.clip(band, 0.0, 1.0)

            if out.shape[2] == 1 and raster.ndim == 2:
                return out[:, :, 0]
            return np.clip(out, 0.0, 1.0)

        elif method == "minmax":
            v_min = np.nanmin(arr)
            v_max = np.nanmax(arr)
            if v_max > v_min:
                return np.clip((arr - v_min) / (v_max - v_min), 0.0, 1.0)
            return np.clip(arr, 0.0, 1.0)

        elif method == "standard":
            mean = np.nanmean(arr, axis=(0, 1), keepdims=True)
            std = np.nanstd(arr, axis=(0, 1), keepdims=True) + 1e-6
            norm = (arr - mean) / std
            # Sigmoid or tanh squashing to [0, 1]
            return 1.0 / (1.0 + np.exp(-norm))

        return np.clip(arr, 0.0, 1.0)

    @staticmethod
    def clip_to_aoi(
        raster: np.ndarray,
        aoi_bbox: Tuple[float, float, float, float],
        full_extent: Tuple[float, float, float, float]
    ) -> np.ndarray:
        """
        Clips raster array according to geographic bounding box.
        aoi_bbox: (min_lat, min_lon, max_lat, max_lon)
        full_extent: (min_lat, min_lon, max_lat, max_lon)
        """
        min_lat_aoi, min_lon_aoi, max_lat_aoi, max_lon_aoi = aoi_bbox
        min_lat_full, min_lon_full, max_lat_full, max_lon_full = full_extent

        h, w = raster.shape[:2]

        lat_range = max_lat_full - min_lat_full
        lon_range = max_lon_full - min_lon_full

        if lat_range <= 0 or lon_range <= 0:
            return raster

        y0 = int(np.clip((max_lat_full - max_lat_aoi) / lat_range * h, 0, h - 1))
        y1 = int(np.clip((max_lat_full - min_lat_aoi) / lat_range * h, y0 + 1, h))
        x0 = int(np.clip((min_lon_aoi - min_lon_full) / lon_range * w, 0, w - 1))
        x1 = int(np.clip((max_lon_aoi - min_lon_full) / lon_range * w, x0 + 1, w))

        cropped = raster[y0:y1, x0:x1]
        return cropped

    @staticmethod
    def prepare_multispectral_stack(
        blue: np.ndarray,
        green: np.ndarray,
        red: np.ndarray,
        nir: Optional[np.ndarray] = None,
        swir: Optional[np.ndarray] = None
    ) -> Dict[str, np.ndarray]:
        """
        Constructs standardized multispectral dictionary and optical RGB array.
        """
        h, w = red.shape[:2]
        bands = {
            "blue": cv2.resize(blue, (w, h)).astype(np.float32),
            "green": cv2.resize(green, (w, h)).astype(np.float32),
            "red": cv2.resize(red, (w, h)).astype(np.float32),
        }

        if nir is not None:
            bands["nir"] = cv2.resize(nir, (w, h)).astype(np.float32)
        else:
            # Synthetic NIR estimation from green and red reflectance
            bands["nir"] = np.clip(bands["green"] * 1.3 - bands["red"] * 0.3, 0.0, 1.0)

        if swir is not None:
            bands["swir"] = cv2.resize(swir, (w, h)).astype(np.float32)
        else:
            bands["swir"] = np.clip(bands["red"] * 0.8 + bands["nir"] * 0.2, 0.0, 1.0)

        # Standard True Color RGB stack
        rgb = np.stack([bands["red"], bands["green"], bands["blue"]], axis=2)
        rgb_norm = SatellitePreprocessor.normalize_reflectance(rgb)

        return {
            "bands": bands,
            "rgb": rgb_norm
        }
