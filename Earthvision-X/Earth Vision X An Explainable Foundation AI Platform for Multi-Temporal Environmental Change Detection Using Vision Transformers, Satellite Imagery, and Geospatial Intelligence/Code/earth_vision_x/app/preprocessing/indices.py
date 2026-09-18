"""
Spectral Index Calculation Module.
Computes Normalized Difference Vegetation Index (NDVI),
Normalized Difference Water Index (NDWI), and
Normalized Difference Built-Up Index (NDBI).
"""

import numpy as np

class SpectralIndexCalculator:
    @staticmethod
    def compute_ndvi(image_rgb: np.ndarray) -> np.ndarray:
        """
        Computes NDVI estimate from RGB satellite image.
        Uses Red channel as Red and Green channel as proxy for NIR if 3-band RGB.
        NDVI = (NIR - Red) / (NIR + Red)
        """
        red = image_rgb[:, :, 0]
        # For RGB imagery, Green acts as pseudo-NIR proxy for vegetation reflectance
        nir = image_rgb[:, :, 1]
        denominator = nir + red + 1e-8
        ndvi = (nir - red) / denominator
        return np.clip(ndvi, -1.0, 1.0)

    @staticmethod
    def compute_ndwi(image_rgb: np.ndarray) -> np.ndarray:
        """
        Computes NDWI estimate.
        NDWI = (Green - NIR) / (Green + NIR)
        """
        green = image_rgb[:, :, 1]
        nir = image_rgb[:, :, 0] # Using Red channel as lower band proxy
        denominator = green + nir + 1e-8
        ndwi = (green - nir) / denominator
        return np.clip(ndwi, -1.0, 1.0)

    @staticmethod
    def compute_ndbi(image_rgb: np.ndarray) -> np.ndarray:
        """
        Computes NDBI estimate (Built-up Index).
        NDBI = (SWIR - NIR) / (SWIR + NIR)
        """
        blue = image_rgb[:, :, 2]
        green = image_rgb[:, :, 1]
        denominator = blue + green + 1e-8
        ndbi = (blue - green) / denominator
        return np.clip(ndbi, -1.0, 1.0)
