"""
VisionTrace AI — Gait Analysis Service
Prototype gait biometric analysis from tracked bounding-box trajectories.
NOTE: This is an academic prototype. Results are NOT legally conclusive.
"""
import numpy as np
from typing import List, Dict, Any


class GaitAnalyzer:
    """
    Computes gait-related features from a track's detection history.
    Features are derived from bounding box movement patterns.
    Future extension: integrate YOLO-Pose keypoint estimation.
    """

    def analyze_track(
        self,
        detections: List[Dict[str, Any]],
        video_fps: float = 25.0,
    ) -> Dict[str, Any]:
        """
        Analyze gait from a list of detection dicts:
        Each dict: { timestamp, bbox: [x1,y1,x2,y2], confidence }

        Returns gait feature dict.
        """
        if len(detections) < 3:
            return self._empty_result()

        sorted_dets = sorted(detections, key=lambda d: d["timestamp"])

        # Centre points
        centres = np.array([
            [(d["bbox"][0] + d["bbox"][2]) / 2,
             (d["bbox"][1] + d["bbox"][3]) / 2]
            for d in sorted_dets
        ])

        timestamps = np.array([d["timestamp"] for d in sorted_dets])
        heights = np.array([d["bbox"][3] - d["bbox"][1] for d in sorted_dets])

        # Walking speed (pixel/sec → normalise by average height)
        if len(centres) > 1:
            diffs = np.diff(centres, axis=0)
            dt = np.diff(timestamps)
            dt = np.where(dt == 0, 1e-3, dt)
            speeds = np.linalg.norm(diffs, axis=1) / dt
            avg_height = np.mean(heights)
            normalised_speed = float(np.mean(speeds) / max(avg_height, 1))
        else:
            normalised_speed = 0.0

        # Vertical oscillation (y-centre variance, normalised by height)
        y_centres = centres[:, 1]
        y_osc = float(np.std(y_centres) / max(np.mean(heights), 1))

        # Stride cadence estimation via zero-crossings of y-velocity
        if len(y_centres) > 4:
            y_vel = np.diff(y_centres)
            zero_crossings = np.where(np.diff(np.sign(y_vel)))[0]
            duration = timestamps[-1] - timestamps[0]
            cadence = len(zero_crossings) / max(duration, 1.0)
        else:
            cadence = 0.0

        # Trajectory consistency (how straight the path is)
        if len(centres) > 2:
            total_dist = np.sum(np.linalg.norm(np.diff(centres, axis=0), axis=1))
            straight_dist = np.linalg.norm(centres[-1] - centres[0])
            consistency = float(straight_dist / max(total_dist, 1.0))
        else:
            consistency = 1.0

        # Height ratio stability (bounding box proportions)
        widths = np.array([d["bbox"][2] - d["bbox"][0] for d in sorted_dets])
        aspect_ratios = heights / np.where(widths == 0, 1, widths)
        torso_stability = float(1.0 - min(np.std(aspect_ratios) / max(np.mean(aspect_ratios), 1), 1.0))

        # Composite gait similarity score (0–1)
        gait_similarity = self._compute_gait_similarity(
            normalised_speed, y_osc, cadence, consistency, torso_stability
        )

        return {
            "walking_speed": round(normalised_speed, 4),
            "cadence": round(cadence, 4),
            "vertical_oscillation": round(y_osc, 4),
            "trajectory_consistency": round(consistency, 4),
            "torso_stability": round(torso_stability, 4),
            "gait_similarity": round(gait_similarity, 4),
            "num_samples": len(sorted_dets),
        }

    def _compute_gait_similarity(
        self,
        speed: float,
        osc: float,
        cadence: float,
        consistency: float,
        stability: float,
    ) -> float:
        """
        Weighted combination of individual gait sub-scores.
        Each sub-score maps a feature value to a quality metric [0,1].
        """
        # Speed score — prefer moderate values (0.01–0.05 normalised)
        speed_score = 1.0 - min(abs(speed - 0.03) / 0.05, 1.0)
        osc_score = max(0.0, 1.0 - osc * 5)
        cadence_score = min(cadence / 2.0, 1.0)

        score = (
            speed_score * 0.25
            + osc_score * 0.20
            + cadence_score * 0.20
            + consistency * 0.20
            + stability * 0.15
        )
        return max(0.0, min(1.0, score))

    def _empty_result(self) -> Dict[str, Any]:
        return {
            "walking_speed": 0.0,
            "cadence": 0.0,
            "vertical_oscillation": 0.0,
            "trajectory_consistency": 0.0,
            "torso_stability": 0.0,
            "gait_similarity": 0.0,
            "num_samples": 0,
        }

    def simulate_for_track(self, track_id: int, base_score: float = 0.82) -> Dict[str, Any]:
        """Deterministic simulated gait for demo mode."""
        rng = np.random.default_rng(seed=track_id * 31)
        gait_sim = max(0.0, min(1.0, base_score + float(rng.uniform(-0.1, 0.1))))
        return {
            "walking_speed": round(float(rng.uniform(0.8, 1.8)), 4),
            "cadence": round(float(rng.uniform(0.6, 1.2)), 4),
            "vertical_oscillation": round(float(rng.uniform(0.02, 0.08)), 4),
            "trajectory_consistency": round(float(rng.uniform(0.70, 0.98)), 4),
            "torso_stability": round(float(rng.uniform(0.75, 0.96)), 4),
            "gait_similarity": round(gait_sim, 4),
            "num_samples": int(rng.integers(15, 60)),
        }
