"""
Fetch and process real photorealistic construction site images and cinematic MP4 videos into uploads/
"""

import os
import ssl
import urllib.request
import cv2
import numpy as np
from pathlib import Path
from config import UPLOADS_IMAGES, UPLOADS_VIDEOS, UPLOADS_DRONE

# Real high-resolution public domain / Unsplash construction stock image URLs
REAL_IMAGE_URLS = {
    "site_brickwork_real.jpg": "https://images.unsplash.com/photo-1590069261209-f8e9b8642343?q=80&w=1200&auto=format&fit=crop",
    "site_foundation_real.jpg": "https://images.unsplash.com/photo-1541888946425-d0fbb186a5b7?q=80&w=1200&auto=format&fit=crop",
    "site_framing_real.jpg": "https://images.unsplash.com/photo-1503387762-592deb58ef4e?q=80&w=1200&auto=format&fit=crop",
    "site_workers_real.jpg": "https://images.unsplash.com/photo-1504307651254-35680f356dfd?q=80&w=1200&auto=format&fit=crop",
    "drone_aerial_real.jpg": "https://images.unsplash.com/photo-1581094794329-c8112a89af12?q=80&w=1200&auto=format&fit=crop"
}

def download_real_images():
    """Downloads real high-resolution construction site photographs."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    ctx = ssl._create_unverified_context()
    
    print("Downloading real construction photographs...")
    for filename, url in REAL_IMAGE_URLS.items():
        try:
            target_path = UPLOADS_IMAGES / filename if "drone" not in filename else UPLOADS_DRONE / filename
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=15) as response, open(target_path, "wb") as out_file:
                out_file.write(response.read())
            print(f"  [OK] Downloaded: {filename}")
        except Exception as e:
            print(f"  [FAIL] Could not download {filename}: {e}")

def create_cinematic_construction_video(image_path: Path, output_video_path: Path, title: str, num_seconds: int = 4):
    """Creates a smooth cinematic pan/zoom MP4 video from a photorealistic construction image."""
    img = cv2.imread(str(image_path))
    if img is None:
        return
        
    img_h, img_w, _ = img.shape
    target_w, target_h = 1280, 720
    fps = 30
    total_frames = fps * num_seconds
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_video_path), fourcc, float(fps), (target_w, target_h))
    
    for i in range(total_frames):
        progress = i / float(total_frames)
        zoom_factor = 1.0 + progress * 0.15 # Smooth zoom effect
        
        crop_w = int(img_w / zoom_factor)
        crop_h = int(img_h / zoom_factor)
        
        start_x = int((img_w - crop_w) * (0.2 + progress * 0.6))
        start_y = int((img_h - crop_h) * (0.2 + progress * 0.6))
        
        start_x = max(0, min(start_x, img_w - crop_w))
        start_y = max(0, min(start_y, img_h - crop_h))
        
        cropped = img[start_y:start_y+crop_h, start_x:start_x+crop_w]
        frame = cv2.resize(cropped, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
        
        # Site Inspection HUD Overlay
        cv2.rectangle(frame, (30, 30), (520, 80), (15, 23, 42), -1)
        cv2.rectangle(frame, (30, 30), (520, 80), (8, 145, 178), 2)
        cv2.putText(frame, f"REAL SITE FOOTAGE - {title}", (45, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (224, 242, 254), 2)
        
        out.write(frame)
        
    out.release()
    print(f"  [OK] Cinematic Video Created: {output_video_path.name}")

def main():
    download_real_images()
    
    brick_img = UPLOADS_IMAGES / "site_brickwork_real.jpg"
    drone_img = UPLOADS_DRONE / "drone_aerial_real.jpg"
    foundation_img = UPLOADS_IMAGES / "site_foundation_real.jpg"
    
    if brick_img.exists():
        create_cinematic_construction_video(brick_img, UPLOADS_VIDEOS / "real_site_brickwork_walkthrough.mp4", "BRICKWORK WALKTHROUGH")
        
    if foundation_img.exists():
        create_cinematic_construction_video(foundation_img, UPLOADS_VIDEOS / "real_site_foundation_walkthrough.mp4", "FOUNDATION INSPECTION")
        
    if drone_img.exists():
        create_cinematic_construction_video(drone_img, UPLOADS_DRONE / "real_drone_aerial_survey.mp4", "AERIAL DRONE SURVEY")

if __name__ == "__main__":
    main()
