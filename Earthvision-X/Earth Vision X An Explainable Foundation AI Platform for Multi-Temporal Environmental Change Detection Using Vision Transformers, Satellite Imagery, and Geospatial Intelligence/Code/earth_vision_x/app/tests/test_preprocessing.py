"""
Unit Tests for Preprocessing Module.
"""

import unittest
import numpy as np
from earth_vision_x.app.preprocessing.indices import SpectralIndexCalculator
from earth_vision_x.app.preprocessing.alignment import ImageAligner
from earth_vision_x.app.preprocessing.cloud import CloudMasker

class TestPreprocessing(unittest.TestCase):
    def test_spectral_indices(self):
        rgb = np.random.rand(256, 256, 3).astype(np.float32)
        ndvi = SpectralIndexCalculator.compute_ndvi(rgb)
        ndwi = SpectralIndexCalculator.compute_ndwi(rgb)
        ndbi = SpectralIndexCalculator.compute_ndbi(rgb)

        self.assertEqual(ndvi.shape, (256, 256))
        self.assertEqual(ndwi.shape, (256, 256))
        self.assertEqual(ndbi.shape, (256, 256))
        self.assertTrue(np.all(ndvi >= -1.0) and np.all(ndvi <= 1.0))

    def test_alignment(self):
        t1 = np.random.rand(256, 256, 3).astype(np.float32)
        t2 = np.random.rand(256, 256, 3).astype(np.float32)
        a1, a2, score = ImageAligner.align_pair(t1, t2)
        self.assertEqual(a1.shape, (256, 256, 3))
        self.assertEqual(a2.shape, (256, 256, 3))

    def test_cloud_masking(self):
        img = np.ones((256, 256, 3), dtype=np.float32) # Bright white image simulating cloud
        mask = CloudMasker.detect_clouds(img)
        self.assertEqual(mask.shape, (256, 256))

if __name__ == "__main__":
    unittest.main()
