"""
VisionTrace AI — Multi-Object Tracker
Tries ByteTrack via supervision; falls back to IoU-based tracking.
"""
import numpy as np
from typing import List, Dict, Any, Optional

# Try supervision (ships ByteTrack)
try:
    import supervision as sv
    SUPERVISION_AVAILABLE = True
except ImportError:
    SUPERVISION_AVAILABLE = False


def _iou(box_a: List[float], box_b: List[float]) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)
    inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)
    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    union = area_a + area_b - inter_area
    return inter_area / union if union > 0 else 0.0


class IoUTracker:
    """Lightweight IoU-based multi-object tracker (no dependencies)."""

    def __init__(self, iou_threshold: float = 0.3, max_age: int = 10):
        self.iou_threshold = iou_threshold
        self.max_age = max_age
        self._tracks: Dict[int, Dict] = {}
        self._next_id = 1

    def update(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        new_tracks = []
        used_track_ids = set()

        for det in detections:
            bbox = det["bbox"]
            conf = det["confidence"]
            best_iou = 0.0
            best_id = None

            for tid, trk in self._tracks.items():
                if tid in used_track_ids:
                    continue
                iou = _iou(bbox, trk["bbox"])
                if iou > best_iou:
                    best_iou = iou
                    best_id = tid

            if best_iou >= self.iou_threshold and best_id is not None:
                self._tracks[best_id].update({"bbox": bbox, "age": 0, "confidence": conf})
                track_id = best_id
                used_track_ids.add(best_id)
            else:
                track_id = self._next_id
                self._tracks[track_id] = {"bbox": bbox, "age": 0, "confidence": conf}
                self._next_id += 1

            new_tracks.append({**det, "track_id": track_id})

        # Age out lost tracks
        to_delete = []
        for tid, trk in self._tracks.items():
            if tid not in used_track_ids:
                trk["age"] += 1
                if trk["age"] > self.max_age:
                    to_delete.append(tid)
        for tid in to_delete:
            del self._tracks[tid]

        return new_tracks


class MultiTargetTracker:
    """
    Wraps ByteTrack (supervision) with IoU fallback.
    Assigns persistent track IDs across frames.
    """

    def __init__(self):
        self._tracker = None
        self._init_tracker()

    def _init_tracker(self):
        if SUPERVISION_AVAILABLE:
            try:
                self._tracker = sv.ByteTracker()
                print("[Tracker] ByteTrack (supervision) initialized.")
            except Exception as e:
                print(f"[Tracker] ByteTrack init failed: {e}. Using IoU tracker.")
                self._tracker = IoUTracker()
        else:
            print("[Tracker] supervision not installed. Using IoU tracker.")
            self._tracker = IoUTracker()

    @property
    def using_bytetrack(self) -> bool:
        return SUPERVISION_AVAILABLE and not isinstance(self._tracker, IoUTracker)

    def update(
        self, detections: List[Dict[str, Any]], frame: Optional[np.ndarray] = None
    ) -> List[Dict[str, Any]]:
        """
        Update tracker with new frame detections.
        Returns detections enriched with 'track_id'.
        """
        if not detections:
            return []

        if self.using_bytetrack:
            return self._update_bytetrack(detections, frame)
        return self._tracker.update(detections)

    def _update_bytetrack(
        self, detections: List[Dict[str, Any]], frame: Optional[np.ndarray]
    ) -> List[Dict[str, Any]]:
        import supervision as sv  # local import for clarity

        bboxes = np.array([d["bbox"] for d in detections], dtype=np.float32)
        confs = np.array([d["confidence"] for d in detections], dtype=np.float32)
        class_ids = np.zeros(len(detections), dtype=int)

        sv_dets = sv.Detections(
            xyxy=bboxes,
            confidence=confs,
            class_id=class_ids,
        )
        tracked = self._tracker.update_with_detections(sv_dets)

        results = []
        for i, (bbox, tid) in enumerate(zip(tracked.xyxy, tracked.tracker_id)):
            conf = float(tracked.confidence[i]) if tracked.confidence is not None else 0.9
            results.append({
                "class": "person",
                "confidence": conf,
                "bbox": bbox.tolist(),
                "track_id": int(tid),
            })
        return results
