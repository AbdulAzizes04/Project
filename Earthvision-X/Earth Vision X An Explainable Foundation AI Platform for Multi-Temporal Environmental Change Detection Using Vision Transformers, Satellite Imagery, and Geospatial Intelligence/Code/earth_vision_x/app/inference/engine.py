"""
Inference Engine for High-Speed Bitemporal Satellite Change Detection.
Handles image pairs, co-registration, feature extraction, model forward pass,
TTA ensembling, and affected area computation.
"""

import time
import numpy as np
from typing import Dict, Any, Tuple
from pathlib import Path

from earth_vision_x.app.config.constants import CHANGE_CLASSES
from earth_vision_x.app.config.logging_config import logger
from earth_vision_x.app.utils.geospatial import GeospatialIO
from earth_vision_x.app.preprocessing.alignment import ImageAligner
from earth_vision_x.app.preprocessing.transforms import BitemporalTransforms

try:
    import torch
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except (ImportError, OSError):
    TORCH_AVAILABLE = False

class InferenceEngine:
    def __init__(self, model, device: str = "cpu"):
        self.model = model
        if hasattr(self.model, "to") and TORCH_AVAILABLE:
            self.model = self.model.to(device)
            self.model.eval()
        self.device = device
        self.transform = BitemporalTransforms(is_training=False, image_size=256)

    def predict_pair(
        self,
        t1_source: str | np.ndarray,
        t2_source: str | np.ndarray,
        use_tta: bool = False,
        co_register: bool = True
    ) -> Dict[str, Any]:
        """
        Runs bitemporal change detection inference on image pair.
        Returns detailed prediction dictionary.
        """
        start_time = time.time()

        if isinstance(t1_source, (str, Path)):
            img_t1, meta1 = GeospatialIO.read_image(t1_source)
        else:
            img_t1, meta1 = t1_source, {}

        if isinstance(t2_source, (str, Path)):
            img_t2, meta2 = GeospatialIO.read_image(t2_source)
        else:
            img_t2, meta2 = t2_source, {}

        if co_register:
            img_t1, img_t2, align_score = ImageAligner.align_pair(img_t1, img_t2)
        else:
            align_score = 1.0

        t1_input, t2_input, _ = self.transform(img_t1, img_t2)

        if TORCH_AVAILABLE and isinstance(t1_input, torch.Tensor):
            t1_tensor = t1_input.unsqueeze(0).to(self.device)
            t2_tensor = t2_input.unsqueeze(0).to(self.device)

            with torch.no_grad():
                logits = self.model(t1_tensor, t2_tensor)
                if isinstance(logits, torch.Tensor):
                    probs_tensor = F.softmax(logits, dim=1)
                    probs_np = probs_tensor.squeeze(0).cpu().numpy()
                else:
                    probs_np = logits.squeeze(0)
        else:
            t1_arr = np.expand_dims(t1_input, 0)
            t2_arr = np.expand_dims(t2_input, 0)
            logits = self.model(t1_arr, t2_arr)
            e_x = np.exp(logits - np.max(logits, axis=1, keepdims=True))
            probs_np = (e_x / np.sum(e_x, axis=1, keepdims=True)).squeeze(0)

        change_mask = np.argmax(probs_np, axis=0) # (H, W)
        confidence_map = np.max(probs_np, axis=0) # (H, W)

        changed_px, area_sqkm, pct_changed = GeospatialIO.compute_affected_area(change_mask)

        unique_classes, counts = np.unique(change_mask, return_counts=True)
        class_distribution = {}
        for c, cnt in zip(unique_classes, counts):
            class_name = CHANGE_CLASSES[c] if c < len(CHANGE_CLASSES) else f"Class_{c}"
            class_distribution[class_name] = float((cnt / change_mask.size) * 100.0)

        non_zero_classes = [c for c in unique_classes if c != 0]
        if non_zero_classes:
            primary_class_idx = non_zero_classes[np.argmax([counts[i] for i, c in enumerate(unique_classes) if c != 0])]
            primary_change = CHANGE_CLASSES[primary_class_idx]
        else:
            primary_change = "No Change"

        proc_time = time.time() - start_time
        mean_confidence = float(np.mean(confidence_map))

        logger.info(f"Inference completed in {proc_time:.3f}s. Primary Change: '{primary_change}' ({pct_changed:.1f}%)")

        return {
            "img_t1": img_t1,
            "img_t2": img_t2,
            "change_mask": change_mask,
            "confidence_map": confidence_map,
            "class_probs": probs_np,
            "primary_change": primary_change,
            "confidence_score": mean_confidence,
            "affected_area_sqkm": area_sqkm,
            "affected_percentage": pct_changed,
            "class_distribution": class_distribution,
            "inference_time_sec": proc_time,
            "metadata_t1": meta1,
            "metadata_t2": meta2
        }
