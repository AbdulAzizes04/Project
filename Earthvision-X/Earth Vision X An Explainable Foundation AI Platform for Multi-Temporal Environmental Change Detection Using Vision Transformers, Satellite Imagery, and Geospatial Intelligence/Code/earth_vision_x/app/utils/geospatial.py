"""
Geospatial Utilities for Satellite Imagery I/O, Coordinate Reference System (CRS) management, and raster conversions.
Handles GeoTIFF, JP2, PNG, JPG reading with fallback mechanisms.
"""

import numpy as np
import cv2
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
from PIL import Image

from earth_vision_x.app.config.logging_config import logger

try:
    import rasterio
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False
    logger.warning("Rasterio not installed; falling back to OpenCV/PIL for satellite raster reading.")

class GeospatialIO:
    @staticmethod
    def read_image(file_path: str | Path, target_size: Optional[Tuple[int, int]] = (256, 256)) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Reads a satellite image (GeoTIFF, JP2, PNG, JPG) and returns (RGB_array, metadata).
        RGB array is float32 normalized [0.0, 1.0], shape (H, W, 3).
        """
        path_str = str(file_path)
        metadata = {
            "file_path": path_str,
            "crs": "EPSG:4326 (Default)",
            "resolution": "10m",
            "channels": 3,
            "width": 256,
            "height": 256,
            "format": Path(file_path).suffix.upper()
        }

        if RASTERIO_AVAILABLE and (path_str.endswith(".tif") or path_str.endswith(".tiff") or path_str.endswith(".jp2")):
            try:
                with rasterio.open(path_str) as src:
                    # Read top 3 bands (or 1 band expanded if single channel)
                    count = src.count
                    if count >= 3:
                        bands = [src.read(i) for i in (1, 2, 3)]
                        img = np.dstack(bands)
                    else:
                        band = src.read(1)
                        img = np.dstack([band, band, band])

                    metadata["crs"] = str(src.crs) if src.crs else "EPSG:4326"
                    metadata["resolution"] = f"{src.res[0]}m"
                    metadata["width"] = src.width
                    metadata["height"] = src.height
                    metadata["channels"] = count

                    # Normalize to uint8 range then float [0, 1]
                    img = img.astype(np.float32)
                    if img.max() > 1.0:
                        img = img / (255.0 if img.max() <= 255 else img.max())

                    if target_size:
                        img = cv2.resize(img, target_size, interpolation=cv2.INTER_LINEAR)

                    return img, metadata
            except Exception as e:
                logger.warning(f"Rasterio read failed for {path_str}: {e}. Falling back to OpenCV/PIL.")

        # Fallback OpenCV / PIL reader for standard formats or when rasterio fails
        img_bgr = cv2.imread(path_str, cv2.IMREAD_COLOR)
        if img_bgr is not None:
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        else:
            pil_img = Image.open(path_str).convert("RGB")
            img_rgb = np.array(pil_img, dtype=np.float32) / 255.0

        metadata["height"], metadata["width"] = img_rgb.shape[:2]
        if target_size:
            img_rgb = cv2.resize(img_rgb, target_size, interpolation=cv2.INTER_LINEAR)

        return img_rgb, metadata

    @staticmethod
    def compute_affected_area(change_mask: np.ndarray, pixel_resolution_m: float = 10.0) -> Tuple[float, float, float]:
        """
        Computes changed area from binary/categorical change mask.
        Returns: (changed_pixels_count, changed_area_sqkm, percentage_changed)
        """
        total_pixels = change_mask.size
        changed_pixels = np.count_nonzero(change_mask > 0)
        pixel_area_sqm = pixel_resolution_m * pixel_resolution_m
        total_area_sqkm = (total_pixels * pixel_area_sqm) / 1e6
        changed_area_sqkm = (changed_pixels * pixel_area_sqm) / 1e6
        percentage = (changed_pixels / total_pixels) * 100.0 if total_pixels > 0 else 0.0

        return float(changed_pixels), float(changed_area_sqkm), float(percentage)
