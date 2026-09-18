"""
Demo Media Generator for BuildVerse AI.
Populates uploads/images, uploads/videos, and uploads/drone with sample images and playable MP4 videos.
"""

import os
import shutil
import cv2
import numpy as np
from pathlib import Path
from config import UPLOADS_IMAGES, UPLOADS_VIDEOS, UPLOADS_DRONE

def create_sample_video(output_path: Path, title: str, num_frames: int = 90):
    """Generates a playable MP4 video with moving site inspection grid."""
    w, h = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, 30.0, (w, h))
    
    for i in range(num_frames):
        # Create dynamic background simulating site camera pan
        frame = np.full((h, w, 3), (245, 247, 250), dtype=np.uint8)
        
        # Draw grid
        offset = (i * 4) % 40
        for x in range(offset, w, 40):
            cv2.line(frame, (x, 0), (x, h), (220, 230, 240), 1)
        for y in range(0, h, 40):
            cv2.line(frame, (0, y), (w, y), (220, 230, 240), 1)
            
        # Draw simulated building structure
        cv2.rectangle(frame, (100, 150), (540, 400), (200, 180, 160), -1)
        cv2.rectangle(frame, (100, 150), (540, 400), (8, 145, 178), 3)
        
        # Moving scanning line
        scan_y = int(150 + (i / num_frames) * 250)
        cv2.line(frame, (100, scan_y), (540, scan_y), (6, 182, 212), 2)
        
        # Overlay text
        cv2.putText(frame, f"BUILDVERSE AI SITE MONITOR - {title}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (15, 23, 42), 2)
        cv2.putText(frame, f"FRAME {i+1}/{num_frames} | SCANNING STRUCTURE...", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (8, 145, 178), 1)
        
        out.write(frame)
        
    out.release()

def main():
    # 1. Source AI generated images if available
    brain_dir = Path(os.path.expanduser("~")) / ".gemini" / "antigravity-ide" / "brain"
    gen_images = list(brain_dir.glob("**/*.png"))
    
    # Copy generated images to uploads/images and uploads/drone
    if gen_images:
        for idx, img_p in enumerate(gen_images[:2]):
            if idx == 0:
                shutil.copy(img_p, UPLOADS_IMAGES / "site_inspection_brickwork.jpg")
                shutil.copy(img_p, UPLOADS_IMAGES / "sample_site.jpg")
            else:
                shutil.copy(img_p, UPLOADS_DRONE / "drone_aerial_scan.jpg")
    
    # 2. Create synthetic OpenCV inspection images as fallback
    for name, phase in [("foundation_scan.jpg", "Foundation Phase"), ("brickwork_scan.jpg", "Brick Work Phase"), ("plastering_scan.jpg", "Plastering Phase")]:
        img = np.full((600, 800, 3), (250, 250, 250), dtype=np.uint8)
        # Background blueprint tint
        cv2.rectangle(img, (50, 50), (750, 550), (240, 245, 250), -1)
        cv2.rectangle(img, (50, 50), (750, 550), (8, 145, 178), 3)
        cv2.putText(img, f"BuildVerse AI Reference Photo: {phase}", (80, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (8, 145, 178), 2)
        cv2.rectangle(img, (120, 150), (680, 480), (216, 182, 8), -1)
        cv2.putText(img, "VERIFIED STRUCTURAL ZONE", (200, 320), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (15, 23, 42), 2)
        cv2.imwrite(str(UPLOADS_IMAGES / name), img)

    # 3. Create Sample MP4 Videos
    create_sample_video(UPLOADS_VIDEOS / "site_walkthrough_inspection.mp4", "WALKTHROUGH FOOTAGE")
    create_sample_video(UPLOADS_DRONE / "drone_survey_flight.mp4", "DRONE AERIAL SURVEY")

    print("Demo reference images and videos populated in uploads/ successfully.")

if __name__ == "__main__":
    main()
