"""
VisionTrace AI — Video Processor Service
Extracts frames from CCTV footage with timestamp mapping.
"""
import cv2
import os
import numpy as np
from typing import List, Dict, Any


class VideoProcessor:
    def __init__(self, output_dir: str = "temp_frames"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def get_video_metadata(self, video_path: str) -> Dict[str, Any]:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps if fps > 0 else 0
        cap.release()

        return {
            "video_name": os.path.basename(video_path),
            "fps": fps,
            "total_frames": total_frames,
            "width": width,
            "height": height,
            "duration": duration,
        }

    def extract_frames(
        self,
        video_path: str,
        target_fps: int = 2,
        progress_callback=None,
    ) -> List[Dict[str, Any]]:
        """
        Extract frames at target_fps and return list of:
        { frame_number, timestamp, frame (np.ndarray) }
        """
        meta = self.get_video_metadata(video_path)
        source_fps = meta["fps"]
        total_frames = meta["total_frames"]

        # How many source frames to skip between extractions
        frame_interval = max(1, int(source_fps / target_fps))

        cap = cv2.VideoCapture(video_path)
        extracted = []
        frame_idx = 0
        extracted_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % frame_interval == 0:
                timestamp = frame_idx / source_fps
                extracted.append({
                    "frame_number": frame_idx,
                    "timestamp": round(timestamp, 3),
                    "frame": frame,
                })
                extracted_count += 1

                if progress_callback and extracted_count % 10 == 0:
                    progress = frame_idx / max(total_frames, 1)
                    progress_callback(progress)

            frame_idx += 1

        cap.release()
        return extracted

    def save_frame(self, frame: np.ndarray, name: str) -> str:
        path = os.path.join(self.output_dir, name)
        cv2.imwrite(path, frame)
        return path

    def crop_person(
        self, frame: np.ndarray, bbox: List[float], padding: int = 10
    ) -> np.ndarray:
        """Crop person from frame given bounding box [x1,y1,x2,y2]."""
        h, w = frame.shape[:2]
        x1 = max(0, int(bbox[0]) - padding)
        y1 = max(0, int(bbox[1]) - padding)
        x2 = min(w, int(bbox[2]) + padding)
        y2 = min(h, int(bbox[3]) + padding)
        return frame[y1:y2, x1:x2]
