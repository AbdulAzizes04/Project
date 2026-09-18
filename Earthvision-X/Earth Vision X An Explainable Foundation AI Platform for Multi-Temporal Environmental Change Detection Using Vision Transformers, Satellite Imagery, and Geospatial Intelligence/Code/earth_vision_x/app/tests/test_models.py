"""
Unit Tests for Vision Transformer Deep Learning Architectures.
"""

import unittest
import torch
from earth_vision_x.app.models.siamese_vit import SiameseViTChangeDetector
from earth_vision_x.app.models.segformer_cd import SegFormerChangeDetector

class TestModels(unittest.TestCase):
    def test_siamese_vit_forward(self):
        model = SiameseViTChangeDetector(num_classes=11, pretrained=False)
        t1 = torch.randn(1, 3, 256, 256)
        t2 = torch.randn(1, 3, 256, 256)
        out = model(t1, t2)
        self.assertEqual(out.shape, (1, 11, 256, 256))

    def test_segformer_forward(self):
        model = SegFormerChangeDetector(num_classes=11)
        t1 = torch.randn(1, 3, 256, 256)
        t2 = torch.randn(1, 3, 256, 256)
        out = model(t1, t2)
        self.assertEqual(out.shape, (1, 11, 256, 256))

if __name__ == "__main__":
    unittest.main()
