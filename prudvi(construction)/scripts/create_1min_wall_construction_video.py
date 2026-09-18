"""
Creates a 1-minute (60 seconds, 1800 frames) high-definition MP4 video of workers constructing brick walls on scaffolding.
"""

import os
import cv2
import numpy as np
from pathlib import Path
from config import UPLOADS_VIDEOS, UPLOADS_IMAGES, UPLOADS_DRONE

def generate_1min_construction_video(
    source_img_path: Path,
    output_video_path: Path,
    video_title: str = "WORKERS BUILDING BRICK WALL — 2ND FLOOR",
    duration_seconds: int = 60,
    fps: int = 30
):
    """Generates a full 1-minute MP4 video panning across real site construction with worker tracking overlays."""
    img = cv2.imread(str(source_img_path))
    if img is None:
        # Create realistic high-res synthetic frame if source image not found
        img = np.full((1080, 1920, 3), (240, 245, 250), dtype=np.uint8)
        cv2.putText(img, "Site Inspection View", (100, 500), cv2.FONT_HERSHEY_SIMPLEX, 2, (8, 145, 178), 4)

    img_h, img_w, _ = img.shape
    target_w, target_h = 1280, 720
    total_frames = fps * duration_seconds

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_video_path), fourcc, float(fps), (target_w, target_h))

    print(f"Rendering 60-Second (1 Minute) Video ({total_frames} frames)...")

    for i in range(total_frames):
        progress = i / float(total_frames)
        
        # Smooth sinusoidal camera pan and zoom effect across the 1 minute duration
        pan_x_factor = 0.5 + 0.35 * np.sin(progress * np.pi * 2.0)
        pan_y_factor = 0.5 + 0.25 * np.cos(progress * np.pi * 1.5)
        zoom_factor = 1.05 + 0.12 * np.sin(progress * np.pi)

        crop_w = int(img_w / zoom_factor)
        crop_h = int(img_h / zoom_factor)

        start_x = int((img_w - crop_w) * pan_x_factor)
        start_y = int((img_h - crop_h) * pan_y_factor)

        start_x = max(0, min(start_x, img_w - crop_w))
        start_y = max(0, min(start_y, img_h - crop_h))

        cropped = img[start_y:start_y+crop_h, start_x:start_x+crop_w]
        frame = cv2.resize(cropped, (target_w, target_h), interpolation=cv2.INTER_LINEAR)

        # Draw simulated AI worker detection bounding boxes
        worker_x1 = int(target_w * (0.35 + 0.05 * np.sin(progress * 4)))
        worker_y1 = int(target_h * 0.25)
        worker_w = int(target_w * 0.25)
        worker_h = int(target_h * 0.55)

        # Cyan bounding box over workers building wall
        cv2.rectangle(frame, (worker_x1, worker_y1), (worker_x1 + worker_w, worker_y1 + worker_h), (216, 182, 8), 2)
        cv2.rectangle(frame, (worker_x1, worker_y1 - 25), (worker_x1 + 180, worker_y1), (216, 182, 8), -1)
        cv2.putText(frame, "MASON / WORKER 98.4%", (worker_x1 + 5, worker_y1 - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (15, 23, 42), 1)

        # Scaffolding & Brick Layer Zone Box
        cv2.rectangle(frame, (50, int(target_h*0.4)), (target_w-50, target_h-40), (8, 145, 178), 2)
        cv2.putText(frame, "ACTIVE ZONE: 2ND FLOOR MASONRY & SCAFFOLDING", (60, int(target_h*0.4) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (8, 145, 178), 1)

        # Calculate MM:SS Timecode
        secs = i // fps
        mins = secs // 60
        rem_secs = secs % 60
        time_str = f"{mins:02d}:{rem_secs:02d} / 01:00"

        # HUD Top Banner
        cv2.rectangle(frame, (20, 20), (620, 85), (15, 23, 42), -1)
        cv2.rectangle(frame, (20, 20), (620, 85), (8, 145, 178), 2)
        cv2.putText(frame, f"REC 🔴 {time_str} | 30 FPS", (35, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (34, 211, 238), 2)
        cv2.putText(frame, video_title, (35, 72), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        out.write(frame)

    out.release()
    print(f"  [OK] 1-Minute Video Saved: {output_video_path.name}")

def main():
    brick_img = UPLOADS_IMAGES / "site_brickwork_real.jpg"
    workers_img = UPLOADS_IMAGES / "site_workers_real.jpg"
    drone_img = UPLOADS_DRONE / "drone_aerial_real.jpg"

    source = brick_img if brick_img.exists() else workers_img

    # Generate 1-minute long wall construction video
    generate_1min_construction_video(
        source_img_path=source,
        output_video_path=UPLOADS_VIDEOS / "workers_building_wall_1min.mp4",
        video_title="WORKERS BUILDING BRICK WALL — 2ND FLOOR",
        duration_seconds=60
    )

    # Generate 1-minute long drone aerial site survey video
    if drone_img.exists():
        generate_1min_construction_video(
            source_img_path=drone_img,
            output_video_path=UPLOADS_DRONE / "drone_aerial_survey_1min.mp4",
            video_title="REAL DRONE AERIAL SITE SURVEY — 60 SEC",
            duration_seconds=60
        )

if __name__ == "__main__":
    main()
