"""
Unit Tests for Evaluation Metrics Suite.
"""

import unittest
import numpy as np
from earth_vision_x.app.utils.metrics import MetricCalculator

class TestMetrics(unittest.TestCase):
    def test_metrics_calculation(self):
        y_true = np.array([0, 1, 1, 0, 1, 0])
        y_pred = np.array([0, 1, 0, 0, 1, 1])
        
        metrics = MetricCalculator.compute_all_metrics(y_true, y_pred)
        self.assertIn("Accuracy", metrics)
        self.assertIn("Precision", metrics)
        self.assertIn("Recall", metrics)
        self.assertIn("F1 Score", metrics)
        self.assertIn("IoU", metrics)
        self.assertGreaterEqual(metrics["Accuracy"], 0.0)
        self.assertLessEqual(metrics["Accuracy"], 1.0)

if __name__ == "__main__":
    unittest.main()
