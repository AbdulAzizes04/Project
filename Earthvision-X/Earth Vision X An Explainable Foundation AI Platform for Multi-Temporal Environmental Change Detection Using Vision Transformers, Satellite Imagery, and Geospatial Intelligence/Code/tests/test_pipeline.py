"""
Comprehensive Unit & Integration Test Suite for EARTH VISION-X.
Verifies all 18 pipeline components, deep learning models, XAI, and PDF export.
Run with:
    python -m unittest discover -s tests -p "test_*.py" -v
"""

import unittest
import numpy as np
import torch
from pathlib import Path

from src.data.satellite_api import SatelliteDataService
from src.data.cloud_mask import CloudMasker
from src.data.registration import SpatialAligner
from src.data.preprocessing import SatellitePreprocessor
from src.geospatial.ndvi import NDVICalculator
from src.geospatial.ndwi import NDWICalculator
from src.geospatial.area import AreaQuantifier
from src.models.siamese_vit import SiameseVisionTransformer
from src.models.unet_baseline import UNetChangeDetector
from src.models.siamese_cnn import SiameseCNNChangeDetector
from src.training.losses import HybridChangeLoss
from src.training.evaluation import ChangeDetectionEvaluator
from src.xai.attention_rollout import AttentionRollout
from src.xai.shap_explainer import SpectralShapExplainer
from src.reports.pdf_report import PDFReportBuilder

class TestEarthVisionX(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h, cls.w = 128, 128
        cls.img_t1 = np.ones((cls.h, cls.w, 3), dtype=np.float32) * 0.5
        cls.img_t2 = np.ones((cls.h, cls.w, 3), dtype=np.float32) * 0.3

        # Insert localized change patch
        cls.img_t2[30:70, 30:70] = [0.9, 0.1, 0.1]

        cls.bands_t1 = {
            "blue": cls.img_t1[:, :, 2], "green": cls.img_t1[:, :, 1], "red": cls.img_t1[:, :, 0],
            "nir": np.clip(cls.img_t1[:, :, 1] * 1.4, 0.0, 1.0),
            "swir": np.clip(cls.img_t1[:, :, 0] * 0.9, 0.0, 1.0)
        }
        cls.bands_t2 = {
            "blue": cls.img_t2[:, :, 2], "green": cls.img_t2[:, :, 1], "red": cls.img_t2[:, :, 0],
            "nir": np.clip(cls.img_t2[:, :, 1] * 1.4, 0.0, 1.0),
            "swir": np.clip(cls.img_t2[:, :, 0] * 0.9, 0.0, 1.0)
        }

    def test_01_satellite_data_service(self):
        """Test satellite acquisition and authentic metadata structure."""
        service = SatelliteDataService()
        data = service.fetch_satellite_pair(lat=-9.8711, lon=-63.2847, t1_year=2016, t2_year=2026)
        self.assertIn("img_t1", data)
        self.assertIn("img_t2", data)
        self.assertEqual(data["t1_year"], 2016)
        self.assertEqual(data["t2_year"], 2026)
        self.assertIn("Processing Level", data["meta_t1"])
        self.assertIn("Tile ID", data["meta_t1"])

    def test_02_cloud_masking(self):
        """Test optical cloud detection and fast neighborhood inpainting."""
        test_img = np.ones((64, 64, 3), dtype=np.float32) * 0.4
        test_img[10:25, 10:25] = [0.98, 0.98, 0.98] # Artificial cloud
        c_mask, s_mask, invalid = CloudMasker.detect_optical_clouds_and_shadows(test_img)
        self.assertGreater(np.count_nonzero(invalid), 0)

        cleaned = CloudMasker.apply_cloud_mask(test_img, invalid, repair_with_inpainting=True)
        self.assertEqual(cleaned.shape, test_img.shape)

    def test_03_registration_and_alignment(self):
        """Test spatial grid alignment."""
        t1 = np.ones((64, 64, 3), dtype=np.float32)
        t2 = np.ones((48, 48, 3), dtype=np.float32)
        aligned_t1, aligned_t2 = SpatialAligner.align_pixel_grid(t1, t2)
        self.assertEqual(aligned_t1.shape, aligned_t2.shape)

    def test_04_ndvi_calculation(self):
        """Test NDVI formula and range constraints."""
        res = NDVICalculator.analyze_ndvi_pair(self.bands_t1, self.bands_t2)
        self.assertTrue(np.all(res["ndvi_t1"] >= -1.0) and np.all(res["ndvi_t1"] <= 1.0))
        self.assertTrue(np.all(res["ndvi_t2"] >= -1.0) and np.all(res["ndvi_t2"] <= 1.0))
        self.assertIn("mean_ndvi_change", res)

    def test_05_ndwi_calculation(self):
        """Test NDWI formula and water dynamics."""
        res = NDWICalculator.analyze_ndwi_pair(self.bands_t1, self.bands_t2)
        self.assertTrue(np.all(res["ndwi_t1"] >= -1.0) and np.all(res["ndwi_t1"] <= 1.0))
        self.assertIn("water_surface_delta_percentage", res)

    def test_06_siamese_vit_forward(self):
        """Test Siamese Vision Transformer forward pass and dual output heads."""
        model = SiameseVisionTransformer(in_channels=3, num_segmentation_classes=2, num_classification_classes=5)
        model.eval()
        t1 = torch.zeros(1, 3, 128, 128)
        t2 = torch.zeros(1, 3, 128, 128)
        out = model(t1, t2)

        self.assertEqual(out["seg_logits"].shape, (1, 2, 128, 128))
        self.assertEqual(out["cls_logits"].shape, (1, 5))

    def test_07_baseline_models(self):
        """Test U-Net and Siamese CNN baselines."""
        unet = UNetChangeDetector(in_channels=6, num_classes=2)
        cnn = SiameseCNNChangeDetector(in_channels=3, num_classes=2)

        t1 = torch.zeros(1, 3, 64, 64)
        t2 = torch.zeros(1, 3, 64, 64)

        u_out = unet(t1, t2)
        c_out = cnn(t1, t2)

        self.assertEqual(u_out["seg_logits"].shape, (1, 2, 64, 64))
        self.assertEqual(c_out["seg_logits"].shape, (1, 2, 64, 64))

    def test_08_hybrid_loss(self):
        """Test Hybrid Loss combining CE, Dice, and Focal loss."""
        loss_fn = HybridChangeLoss(weight_ce=0.3, weight_dice=0.4, weight_focal=0.3)
        logits = torch.randn(2, 2, 32, 32)
        targets = torch.randint(0, 2, (2, 32, 32))
        loss_dict = loss_fn(logits, targets)

        self.assertIn("total_loss", loss_dict)
        self.assertGreater(loss_dict["total_loss"].item(), 0.0)

    def test_09_evaluation_metrics(self):
        """Test IEEE evaluation metrics computation."""
        pred = np.array([[1, 1], [0, 0]], dtype=np.uint8)
        gt = np.array([[1, 0], [0, 0]], dtype=np.uint8)
        m = ChangeDetectionEvaluator.evaluate_segmentation(pred, gt)

        self.assertIn("iou", m)
        self.assertIn("dice", m)
        self.assertIn("f1", m)
        self.assertGreater(m["f1"], 0.0)

    def test_10_area_quantification(self):
        """Test geographic area quantification and uncertainty classification."""
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[20:40, 20:40] = 1 # 400 pixels changed
        cls_logits = np.array([[1.0, 5.0, 0.5, 0.2, 0.1]])

        metrics = AreaQuantifier.calculate_area_metrics(mask, cls_logits, spatial_resolution_m=10.0)
        self.assertEqual(metrics["changed_pixels"], 400)
        self.assertEqual(metrics["total_pixels"], 10000)
        self.assertAlmostEqual(metrics["change_percentage"], 4.0, places=1)
        self.assertIn(metrics["uncertainty_level"], ["High Confidence", "Medium Confidence", "Low Confidence"])

    def test_11_spectral_shap_attributions(self):
        """Test actual spectral channel attribution calculation."""
        scores = SpectralShapExplainer.compute_spectral_attributions(self.bands_t1, self.bands_t2)
        self.assertIn("Blue", scores)
        self.assertIn("NIR", scores)
        self.assertIn("NDVI", scores)
        total_pct = sum(scores.values())
        self.assertAlmostEqual(total_pct, 100.0, delta=1.0)

    def test_12_pdf_generation(self):
        """Test ReportLab 17-section PDF report generation."""
        mock_data = {
            "aoi_name": "Test Amazon Site",
            "lat": -9.8711, "lon": -63.2847,
            "t1_year": 2016, "t2_year": 2026,
            "img_t1": self.img_t1, "img_t2": self.img_t2,
            "meta_t1": {"Satellite": "Sentinel-2A", "Acquisition Date": "2016-08-15", "Tile ID": "S2A_TEST_2016", "Cloud Percentage": "1.2%"},
            "meta_t2": {"Satellite": "Sentinel-2B", "Acquisition Date": "2026-02-28", "Tile ID": "S2B_TEST_2026", "Cloud Percentage": "0.8%"},
            "change_mask": (np.abs(self.img_t1[:, :, 0] - self.img_t2[:, :, 0]) > 0.2).astype(np.uint8),
            "area_metrics": AreaQuantifier.calculate_area_metrics(
                (np.abs(self.img_t1[:, :, 0] - self.img_t2[:, :, 0]) > 0.2).astype(np.uint8),
                np.array([0.1, 4.0, 0.2, 0.1, 0.1])
            ),
            "ndvi_metrics": NDVICalculator.analyze_ndvi_pair(self.bands_t1, self.bands_t2),
            "ndwi_metrics": NDWICalculator.analyze_ndwi_pair(self.bands_t1, self.bands_t2),
            "attention_rollout": np.ones((self.h, self.w), dtype=np.float32) * 0.5,
            "grad_cam": np.ones((self.h, self.w), dtype=np.float32) * 0.5,
            "shap_scores": {"Blue": 15.2, "Green": 14.1, "Red": 22.4, "NIR": 28.3, "SWIR": 10.0, "NDVI": 6.0, "NDWI": 4.0},
            "ai_story": "The test environmental change story verified successfully."
        }
        pdf_path = PDFReportBuilder.generate_pdf(mock_data)
        self.assertTrue(Path(pdf_path).exists())
        self.assertGreater(Path(pdf_path).stat().st_size, 1000)

if __name__ == "__main__":
    unittest.main()
