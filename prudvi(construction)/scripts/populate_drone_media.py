"""
Downloads real drone aerial construction photographs and generates 1-minute drone MP4 survey video into uploads/drone/
"""

import os
import ssl
import urllib.request
import cv2
import numpy as np
from pathlib import Path
from config import UPLOADS_DRONE

DRONE_URLS = {
    "real_drone_aerial_site_1.jpg": "https://images.unsplash.com/photo-1581094794329-c8112a89af12?q=80&w=1200&auto=format&fit=crop",
    "real_drone_aerial_site_2.jpg": "https://images.unsplash.com/photo-1541888946425-d0fbb186a5b7?q=80&w=1200&auto=format&fit=crop",
    "real_drone_aerial_site_3.jpg": "https://images.unsplash.com/photo-1503387762-592deb58ef4e?q=80&w=1200&auto=format&fit=crop"
}

def download_drone_images():
    headers = {"User-Agent": "Mozilla/5.0"}
    ctx = ssl._create_unverified_context()
    
    print("Downloading real drone aerial site photographs...")
    for filename, url in DRONE_URLS.items():
        try:
            target_path = UPLOADS_DRONE / filename
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=15) as response, open(target_path, "wb") as out_file:
                out_file.write(response.read())
            print(f"  [OK] Drone photo saved: {filename}")
        except Exception as e:
            print(f"  [FAIL] Failed {filename}: {e}")

def create_1min_drone_video():
    img_path = UPLOADS_DRONE / "real_drone_aerial_site_1.jpg"
    if not img_path.exists():
        return
        
    img = cv2.imread(str(img_path))
    if img is None:
        return
        
    img_h, img_w, _ = img.shape
    target_w, target_h = 1280, 720
    fps = 30
    duration_secs = 60
    total_frames = fps * duration_secs
    
    output_path = UPLOADS_DRONE / "drone_aerial_survey_1min.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, float(fps), (target_w, target_h))
    
    print(f"Rendering 60-Second Drone Video ({total_frames} frames)...")
    
    for i in range(total_frames):
        progress = i / float(total_frames)
        zoom_factor = 1.0 + 0.15 * np.sin(progress * np.pi)
        
        crop_w = int(img_w / zoom_factor)
        crop_h = int(img_h / zoom_factor)
        
        start_x = int((img_w - crop_w) * (0.1 + progress * 0.8))
        start_y = int((img_h - crop_h) * (0.1 + progress * 0.8))
        
        start_x = max(0, min(start_x, img_w - crop_w))
        start_y = max(0, min(start_y, img_h - crop_h))
        
        cropped = img[start_y:start_y+crop_h, start_x:start_x+crop_w]
        frame = cv2.resize(cropped, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
        
        # Drone HUD Overlay
        cv2.rectangle(frame, (20, 20), (550, 85), (15, 23, 42), -1)
        cv2.rectangle(frame, (20, 20), (550, 85), (8, 145, 178), 2)
        
        secs = i // fps
        mins = secs // 60
        rem_secs = secs % 60
        time_str = f"{mins:02d}:{rem_secs:02d} / 01:00"
        
        cv2.putText(frame, f"DRONE AERIAL CAM 1 - {time_str}", (35, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (34, 211, 238), 2)
        cv2.putText(frame, "TOP-DOWN SITE SURVEY | ALT: 120 FT", (35, 74), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Crosshair center mark
        cx, cy = target_w // 2, target_h // 2
        cv2.line(frame, (cx - 20, cy), (cx + 20, cy), (8, 145, 178), 2)
        cv2.line(frame, (cx, cy - 20), (cx, cy + 20), (8, 145, 178), 2)
        
        out.write(frame)
        
    out.release()
    print("  [OK] Drone 1-minute MP4 survey video saved!")

def main():
    download_drone_images()
    create_1min_drone_video()

if __name__ == "__main__":
    main()
