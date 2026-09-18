import numpy as np
from typing import List, Dict, Any, Tuple

class SimpleTracker:
    """
    Forensic centroid & IoU multi-object tracker.
    Maintains persistent track IDs across frames and calculates
    trajectories, velocities, and total appearance duration.
    """
    def __init__(self, max_lost: int = 30, iou_thresh: float = 0.3):
        self.next_track_id = 1
        self.tracks = {} # track_id -> dict with history, bboxes, lost_count
        self.max_lost = max_lost
        self.iou_thresh = iou_thresh

    def _compute_iou(self, boxA: List[float], boxB: List[float]) -> float:
        # box: [x, y, w, h]
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[0] + boxA[2], boxB[0] + boxB[2])
        yB = min(boxA[1] + boxA[3], boxB[1] + boxB[3])

        interW = max(0.0, xB - xA)
        interH = max(0.0, yB - yA)
        interArea = interW * interH

        boxAArea = boxA[2] * boxA[3]
        boxBArea = boxB[2] * boxB[3]
        unionArea = boxAArea + boxBArea - interArea

        if unionArea <= 0:
            return 0.0
        return interArea / unionArea

    def update(self, detections: List[Dict[str, Any]], timestamp: str, frame_num: int, camera_id: str = "Camera 01") -> List[Dict[str, Any]]:
        """
        Matches detections to existing tracks or assigns new track IDs.
        """
        matched_tracks = []
        unmatched_dets = list(range(len(detections)))
        unmatched_track_ids = list(self.tracks.keys())

        # Match using IoU
        if self.tracks and detections:
            cost_matrix = np.zeros((len(unmatched_track_ids), len(detections)), dtype=float)
            for i, tid in enumerate(unmatched_track_ids):
                last_box = self.tracks[tid]["last_bbox"]
                for j, det in enumerate(detections):
                    cost_matrix[i, j] = self._compute_iou(last_box, det["bbox_norm"])

            # Greedy match
            while True:
                if cost_matrix.size == 0 or np.max(cost_matrix) < self.iou_thresh:
                    break
                max_idx = np.unravel_index(np.argmax(cost_matrix), cost_matrix.shape)
                tid = unmatched_track_ids[max_idx[0]]
                det_idx = max_idx[1]

                # Update matched track
                det = detections[det_idx]
                det["track_id"] = tid
                self.tracks[tid]["last_bbox"] = det["bbox_norm"]
                self.tracks[tid]["last_seen_frame"] = frame_num
                self.tracks[tid]["last_seen_time"] = timestamp
                self.tracks[tid]["lost_count"] = 0
                self.tracks[tid]["history"].append({
                    "frame": frame_num,
                    "timestamp": timestamp,
                    "bbox": det["bbox_norm"],
                    "camera_id": camera_id
                })
                matched_tracks.append(det)

                # Invalidate row and column
                cost_matrix[max_idx[0], :] = -1.0
                cost_matrix[:, max_idx[1]] = -1.0
                if det_idx in unmatched_dets:
                    unmatched_dets.remove(det_idx)
                if tid in unmatched_track_ids:
                    unmatched_track_ids.remove(tid)

        # Handle unmatched detections -> register new tracks
        for det_idx in unmatched_dets:
            det = detections[det_idx]
            new_id = self.next_track_id
            self.next_track_id += 1
            det["track_id"] = new_id

            self.tracks[new_id] = {
                "track_id": new_id,
                "first_seen_time": timestamp,
                "first_seen_frame": frame_num,
                "last_seen_time": timestamp,
                "last_seen_frame": frame_num,
                "last_bbox": det["bbox_norm"],
                "lost_count": 0,
                "camera_ids": {camera_id},
                "history": [{
                    "frame": frame_num,
                    "timestamp": timestamp,
                    "bbox": det["bbox_norm"],
                    "camera_id": camera_id
                }]
            }
            matched_tracks.append(det)

        # Age remaining unmatched tracks
        to_delete = []
        for tid in unmatched_track_ids:
            self.tracks[tid]["lost_count"] += 1
            if self.tracks[tid]["lost_count"] > self.max_lost:
                to_delete.append(tid)

        for tid in to_delete:
            del self.tracks[tid]

        return matched_tracks
