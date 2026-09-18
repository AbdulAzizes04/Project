import os
import shutil
import cv2
import numpy as np

def create_cctv_video(output_path, camera_name, duration_sec=6, fps=25, width=1280, height=720, camera_type="gate"):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    total_frames = duration_sec * fps
    
    np.random.seed(42)
    
    for f in range(total_frames):
        # Base background with CCTV room/hallway/gate appearance
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Draw background architecture
        if camera_type == "gate":
            # Dark exterior / security checkpoint
            frame[:] = (20, 26, 24) # dark bluish-green night surveillance
            # Road / gate lines
            cv2.rectangle(frame, (0, int(height*0.65)), (width, height), (35, 40, 38), -1)
            cv2.line(frame, (100, int(height*0.65)), (300, height), (50, 60, 55), 3)
            cv2.line(frame, (width-100, int(height*0.65)), (width-300, height), (50, 60, 55), 3)
            # Security booth
            cv2.rectangle(frame, (100, int(height*0.25)), (350, int(height*0.65)), (40, 48, 45), -1)
            cv2.rectangle(frame, (130, int(height*0.3)), (220, int(height*0.45)), (80, 110, 100), -1)
            
            # Moving person (Candidate #07) entering from left to right
            progress = f / total_frames
            px = int(250 + progress * 550)
            py = int(height * 0.45 + (1 - progress * 0.1) * (height * 0.15))
            pw, ph = 60, 140
            
            # Person silhouette with dark tactical hoodie
            # Legs
            leg_swing = int(np.sin(f * 0.6) * 12)
            cv2.line(frame, (px + 20, py + ph - 20), (px + 10 + leg_swing, py + ph), (15, 18, 22), 8)
            cv2.line(frame, (px + 40, py + ph - 20), (px + 50 - leg_swing, py + ph), (15, 18, 22), 8)
            # Torso / hoodie
            cv2.rectangle(frame, (px + 10, py + 35), (px + 50, py + ph - 20), (22, 25, 30), -1)
            # Head with mask/hood
            cv2.circle(frame, (px + 30, py + 20), 16, (18, 20, 24), -1)
            
            # Neural Bounding box HUD overlay
            cv2.rectangle(frame, (px, py), (px + pw, py + ph), (0, 229, 255), 2)
            cv2.putText(frame, "POI #07 [0.94]", (px, py - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 229, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, "MASKED", (px, py + ph + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 100, 255), 1, cv2.LINE_AA)

        elif camera_type == "vault":
            # Interior hallway / corridor
            frame[:] = (18, 20, 28)
            # Corridor perspective
            pts = np.array([[int(width*0.35), int(height*0.25)], [int(width*0.65), int(height*0.25)],
                            [int(width*0.85), height], [int(width*0.15), height]], np.int32)
            cv2.fillPoly(frame, [pts], (30, 32, 42))
            # Vault door in distance
            cv2.rectangle(frame, (int(width*0.42), int(height*0.28)), (int(width*0.58), int(height*0.62)), (50, 55, 70), -1)
            cv2.circle(frame, (int(width*0.5), int(height*0.45)), 25, (75, 80, 100), 2)
            
            # Moving subject approaching vault
            progress = f / total_frames
            px = int(width * 0.38 + np.sin(progress * 3.14) * 80)
            py = int(height * 0.38 + progress * 80)
            pw, ph = int(50 + progress * 40), int(120 + progress * 90)
            
            # Silhouette
            cv2.rectangle(frame, (px + int(pw*0.2), py + int(ph*0.3)), (px + int(pw*0.8), py + int(ph*0.85)), (25, 25, 32), -1)
            cv2.circle(frame, (px + int(pw*0.5), py + int(ph*0.2)), int(pw*0.25), (20, 20, 25), -1)
            
            # Bounding box
            cv2.rectangle(frame, (px, py), (px + pw, py + ph), (0, 229, 255), 2)
            cv2.putText(frame, "POI #07 [0.96] LOITERING", (px - 20, py - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 229, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, "GAIT-007 [92%]", (px, py + ph + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 120), 1, cv2.LINE_AA)

        else: # perimeter
            # West perimeter fence & loading bay
            frame[:] = (15, 22, 20)
            cv2.rectangle(frame, (0, int(height*0.5)), (width, height), (28, 35, 32), -1)
            # Fence posts
            for fx in range(50, width, 80):
                cv2.line(frame, (fx, int(height*0.3)), (fx, int(height*0.7)), (45, 55, 50), 2)
            cv2.line(frame, (0, int(height*0.35)), (width, int(height*0.35)), (55, 65, 60), 1)
            cv2.line(frame, (0, int(height*0.5)), (width, int(height*0.5)), (55, 65, 60), 1)
            
            # Fleeing subject moving swiftly
            progress = f / total_frames
            px = int(width * 0.7 - progress * 450)
            py = int(height * 0.42)
            pw, ph = 55, 130
            
            cv2.rectangle(frame, (px + 10, py + 30), (px + 45, py + ph - 20), (20, 22, 26), -1)
            cv2.circle(frame, (px + 28, py + 18), 15, (16, 18, 20), -1)
            
            cv2.rectangle(frame, (px, py), (px + pw, py + ph), (0, 229, 255), 2)
            cv2.putText(frame, "POI #07 [0.89] RAPID TRANSIT", (px - 30, py - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 229, 255), 1, cv2.LINE_AA)

        # Subtle noise / grain
        noise = np.random.randint(-8, 8, frame.shape, dtype=np.int16)
        frame = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)

        # Scanlines
        frame[::4, :, :] = (frame[::4, :, :] * 0.85).astype(np.uint8)

        # CCTV HUD Overlays
        # Top Left: Camera Info & REC icon
        cv2.circle(frame, (35, 35), 8, (0, 0, 255), -1)
        cv2.putText(frame, "REC  [LIVE-FEED]", (52, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, camera_name, (35, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 229, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "1920x1080 @ 30FPS | H.264 FORENSIC STREAM", (35, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1, cv2.LINE_AA)

        # Top Right: Timestamp
        sec = f / fps
        time_str = f"2026-09-08  19:3{int(sec//60)}:{int(sec%60):02d}.{int((sec%1)*100):02d} UTC"
        cv2.putText(frame, time_str, (width - 430, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "VISIONTRACE AI - FORENSIC HUB v1.0", (width - 430, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 229, 255), 1, cv2.LINE_AA)

        # Bottom Border info
        cv2.rectangle(frame, (0, height - 35), (width, height), (10, 12, 16), -1)
        cv2.putText(frame, "STATUS: AI-ASSISTED TRACKING ACTIVE | ENCRYPTION: SHA-256 | JURISDICTION: METROPOLITAN PRECINCT", 
                    (25, height - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (120, 180, 160), 1, cv2.LINE_AA)

        out.write(frame)

    out.release()
    print(f"Generated video: {output_path}")

def main():
    base_dir = r"d:\projects\vision trace(supreethi)"
    uploads_vid = os.path.join(base_dir, "uploads", "videos")
    uploads_img = os.path.join(base_dir, "uploads", "images")
    proc_clips = os.path.join(base_dir, "processed", "clips")
    proc_frames = os.path.join(base_dir, "processed", "frames")
    
    os.makedirs(uploads_vid, exist_ok=True)
    os.makedirs(uploads_img, exist_ok=True)
    os.makedirs(proc_clips, exist_ok=True)
    os.makedirs(proc_frames, exist_ok=True)

    # 1. Generate CCTV Sample Videos
    create_cctv_video(os.path.join(uploads_vid, "cam01_gate.mp4"), "CAM 01: NORTH GATE CHECKPOINT", duration_sec=5, camera_type="gate")
    create_cctv_video(os.path.join(uploads_vid, "cam02_vault.mp4"), "CAM 02: VAULT ACCESS CORRIDOR", duration_sec=5, camera_type="vault")
    create_cctv_video(os.path.join(uploads_vid, "cam03_perimeter.mp4"), "CAM 03: WEST PERIMETER EXIT", duration_sec=5, camera_type="perimeter")
    create_cctv_video(os.path.join(uploads_vid, "sample_cctv_heist.mp4"), "CAM 04: SECURITY LOBBY DOCK", duration_sec=5, camera_type="vault")
    
    # Also create evidence clip in processed/clips
    create_cctv_video(os.path.join(proc_clips, "Person_Of_Interest_07_Evidence.mp4"), "FORENSIC EVIDENCE COMPILATION: POI #07", duration_sec=6, camera_type="vault")
    create_cctv_video(os.path.join(proc_clips, "cam01_gate_enhanced.mp4"), "CLAHE ENHANCED: CAM 01 GATE", duration_sec=5, camera_type="gate")

    # 2. Copy reference suspect images
    brain_dir = r"C:\Users\shaik\.gemini\antigravity-ide\brain\a9e6195c-ab65-4858-8531-57deaca2e3ec"
    img1 = os.path.join(brain_dir, "suspect_photo_ref_1788919294822.jpg")
    img2 = os.path.join(brain_dir, "suspect_poi_photo_1788919314065.jpg")

    if os.path.exists(img1):
        shutil.copy(img1, os.path.join(uploads_img, "suspect_reference_photo.jpg"))
        shutil.copy(img1, os.path.join(uploads_img, "suspect_candidate_07_masked.jpg"))
        shutil.copy(img1, os.path.join(proc_frames, "crop_poi_CASE-2026-089_track_7.jpg"))
        print(f"Copied masked suspect photo to uploads/images and processed/frames")

    if os.path.exists(img2):
        shutil.copy(img2, os.path.join(uploads_img, "suspect_unmasked_reference.jpg"))
        shutil.copy(img2, os.path.join(uploads_img, "reference_person_02.jpg"))
        shutil.copy(img2, os.path.join(proc_frames, "crop_poi_CASE-2026-089_track_2.jpg"))
        print(f"Copied unmasked suspect photo to uploads/images and processed/frames")

    print("Sample media setup complete!")

if __name__ == "__main__":
    main()
