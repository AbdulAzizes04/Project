"""
Quantitative Change and Spatial Area Analysis Module for EARTH VISION-X.
Calculates:
- Total AOI Area (km²)
- Changed Area (km²)
- Unchanged Area (km²)
- Change Percentage (%)
- Category-level breakdown (affected pixels, area, percentage, confidence)
- Uncertainty categorization (High, Medium, Low Confidence)
"""

import numpy as np
from typing import Dict, Any, List

class AreaQuantifier:
    """
    Computes rigorous geographic area metrics from pixel masks and spatial resolution.
    """

    @staticmethod
    def calculate_area_metrics(
        change_mask: np.ndarray,
        cls_logits: np.ndarray,
        spatial_resolution_m: float = 10.0,
        class_names: List[str] = None
    ) -> Dict[str, Any]:
        """
        Calculates exact surface areas in square kilometers based on satellite ground resolution.
        """
        if class_names is None:
            class_names = ["No Change", "Deforestation", "Urban Expansion", "Water Body Change", "Vegetation Loss"]

        h, w = change_mask.shape[:2]
        total_pixels = h * w

        # Area per pixel in square kilometers: (10m * 10m) = 100 m² = 1e-4 km²
        pixel_area_km2 = (spatial_resolution_m * spatial_resolution_m) / 1_000_000.0

        total_area_km2 = total_pixels * pixel_area_km2
        changed_pixels = int(np.count_nonzero(change_mask > 0))
        unchanged_pixels = total_pixels - changed_pixels

        changed_area_km2 = changed_pixels * pixel_area_km2
        unchanged_area_km2 = unchanged_pixels * pixel_area_km2
        change_pct = (changed_pixels / total_pixels) * 100.0 if total_pixels > 0 else 0.0

        # Primary change category and confidence estimation
        # Softmax over classification logits
        exp_logits = np.exp(cls_logits - np.max(cls_logits))
        probs = exp_logits / (np.sum(exp_logits) + 1e-8)
        if probs.ndim > 1:
            probs = probs[0]

        # Ignore class 0 ("No Change") when picking primary detected change
        if len(probs) > 1:
            change_probs = probs[1:]
            primary_idx = int(np.argmax(change_probs)) + 1
            primary_class = class_names[primary_idx] if primary_idx < len(class_names) else "Environmental Change"
            confidence = float(probs[primary_idx])
        else:
            primary_class = "No Change"
            confidence = float(probs[0])

        # Category breakdown
        category_breakdown = []
        for idx, cname in enumerate(class_names):
            c_prob = float(probs[idx]) if idx < len(probs) else 0.0
            if idx == 0:
                c_pixels = unchanged_pixels
            else:
                # Distribute changed pixels according to relative probability
                sub_sum = sum(probs[1:]) + 1e-8
                c_pixels = int(changed_pixels * (probs[idx] / sub_sum))

            c_area = c_pixels * pixel_area_km2
            c_pct = (c_pixels / total_pixels) * 100.0

            category_breakdown.append({
                "category": cname,
                "affected_pixels": c_pixels,
                "affected_area_km2": round(c_area, 3),
                "percentage": round(c_pct, 2),
                "confidence": round(c_prob * 100.0, 1)
            })

        # Uncertainty Classification
        if confidence >= 0.85:
            uncertainty_label = "High Confidence"
        elif confidence >= 0.65:
            uncertainty_label = "Medium Confidence"
        else:
            uncertainty_label = "Low Confidence"

        return {
            "total_pixels": total_pixels,
            "changed_pixels": changed_pixels,
            "unchanged_pixels": unchanged_pixels,
            "total_area_km2": round(total_area_km2, 3),
            "changed_area_km2": round(changed_area_km2, 3),
            "unchanged_area_km2": round(unchanged_area_km2, 3),
            "change_percentage": round(change_pct, 2),
            "primary_change": primary_class,
            "confidence_score": round(confidence, 4),
            "confidence_percentage": round(confidence * 100.0, 2),
            "uncertainty_level": uncertainty_label,
            "category_breakdown": category_breakdown
        }
