"""
VisionTrace AI — Multi-Modal Score Fusion
Combines Re-ID, Gait, Clothing, and Face scores with configurable weights.
"""
from typing import Dict, Any, Optional


WEIGHT_PRESETS = {
    "default": {"reid": 0.40, "gait": 0.25, "face": 0.20, "clothing": 0.15},
    "reid_heavy": {"reid": 0.55, "gait": 0.20, "face": 0.15, "clothing": 0.10},
    "gait_heavy": {"reid": 0.30, "gait": 0.45, "face": 0.15, "clothing": 0.10},
    "no_face": {"reid": 0.50, "gait": 0.30, "face": 0.00, "clothing": 0.20},
}


def classify_confidence(score: float) -> str:
    """Map a [0,1] score to an evidence rating label."""
    pct = score * 100
    if pct >= 90:
        return "HIGH"
    elif pct >= 70:
        return "MEDIUM"
    return "LOW"


class SimilarityFusion:

    def __init__(self, preset: str = "default"):
        self.weights = WEIGHT_PRESETS.get(preset, WEIGHT_PRESETS["default"])

    def set_weights(self, reid: float = 0.40, gait: float = 0.25,
                    face: float = 0.20, clothing: float = 0.15):
        total = reid + gait + face + clothing
        if total == 0:
            raise ValueError("Weights must sum to a positive value.")
        self.weights = {
            "reid": reid / total,
            "gait": gait / total,
            "face": face / total,
            "clothing": clothing / total,
        }

    def fuse(
        self,
        reid_score: float,
        gait_score: float,
        clothing_score: float,
        face_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Compute the weighted multi-modal confidence score.

        Args:
            reid_score:     Person re-identification similarity [0, 1]
            gait_score:     Gait analysis similarity [0, 1]
            clothing_score: Clothing/appearance similarity [0, 1]
            face_score:     Face recognition similarity [0, 1] (optional)

        Returns dict with 'final_score', 'evidence_rating', 'breakdown'.
        """
        w = self.weights.copy()

        # If face is unavailable, redistribute its weight to re-id
        if face_score is None:
            face_score = 0.0
            bonus = w["face"]
            w["reid"] += bonus * 0.6
            w["gait"] += bonus * 0.4
            w["face"] = 0.0

        final_score = (
            reid_score * w["reid"]
            + gait_score * w["gait"]
            + face_score * w["face"]
            + clothing_score * w["clothing"]
        )
        final_score = round(max(0.0, min(1.0, final_score)), 4)

        return {
            "reid_score": round(reid_score, 4),
            "gait_score": round(gait_score, 4),
            "clothing_score": round(clothing_score, 4),
            "face_score": round(face_score, 4),
            "final_score": final_score,
            "confidence_pct": round(final_score * 100, 2),
            "evidence_rating": classify_confidence(final_score),
            "weights_used": w,
        }
