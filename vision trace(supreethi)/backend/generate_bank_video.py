import os
import shutil
import cv2
import numpy as np

def generate_bank_cctv_video():
    brain_dir = r"C:\Users\shaik\.gemini\antigravity-ide\brain\a9e6195c-ab65-4858-8531-57deaca2e3ec"
    suspect_img_path = os.path.join(brain_dir, "bank_suspect_ref_1788919615004.jpg")
    
    base_dir = r"d:\projects\vision trace(supreethi)"
    uploads_vid = os.path.join(base_dir, "uploads", "videos")
    uploads_img = os.path.join(base_dir, "uploads", "images")
    proc_clips = os.path.join(base_dir, "processed", "clips")
    proc_frames = os.path.join(base_dir, "processed", "frames")

    os.makedirs(uploads_vid, exist_ok=True)
    os.makedirs(uploads_img, exist_ok=True)
    os.makedirs(proc_clips, exist_ok=True)
    os.makedirs(proc_frames, exist_ok=True)

    # Copy suspect image
    if os.path.exists(suspect_img_path):
        shutil.copy(suspect_img_path, os.path.join(uploads_img, "bank_suspect_reference.jpg"))
        shutil.copy(suspect_img_path, os.path.join(uploads_img, "suspect_bank_loitering.jpg"))
        shutil.copy(suspect_img_path, os.path.join(proc_frames, "bank_suspect_crop.jpg"))
        print("Copied bank suspect image to uploads and processed folders.")

    # Load suspect image if available to extract appearance features or background
    ref_bgr = cv2.imread(suspect_img_path) if os.path.exists(suspect_img_path) else None

    output_path = os.path.join(uploads_vid, "bank_cctv_roaming_suspect.mp4")
    output_path_alt = os.path.join(uploads_vid, "cam_bank_lobby.mp4")
    output_clip_path = os.path.join(proc_clips, "Bank_Reconnaissance_Suspect_Evidence.mp4")

    width, height = 1280, 720
    fps = 25
    duration_sec = 12
    total_frames = duration_sec * fps

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Path coordinates for the suspect:
    # 1. Enters from Entrance (right/door)
    # 2. Walks towards the Teller Counter (left)
    # 3. Loiters and inspects counter / barrier
    # 4. Turns and roams towards the ATM vestibule (center-right)
    # 5. Pauses, scans surroundings / ceiling camera
    # 6. Moves back towards exit and leaves

    for f in range(total_frames):
        # Create bank lobby background
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Upper wall (light beige bank interior)
        frame[0:int(height*0.55), :] = (205, 215, 215) # soft bank lobby wall
        
        # Polished marble tiled floor (lower half)
        frame[int(height*0.55):, :] = (175, 185, 188)
        
        # Floor tile grid lines with perspective
        for row_y in range(int(height*0.55), height, 40):
            cv2.line(frame, (0, row_y), (width, row_y), (150, 160, 165), 1)
        for col_x in range(0, width + 400, 90):
            cv2.line(frame, (col_x, int(height*0.55)), (col_x - 180, height), (150, 160, 165), 1)

        # Bank Teller Counter on Left
        # Counter base (wood mahogany finish)
        cv2.rectangle(frame, (0, int(height*0.48)), (420, height), (35, 45, 80), -1)
        # Granite counter top
        cv2.rectangle(frame, (0, int(height*0.45)), (440, int(height*0.49)), (90, 105, 120), -1)
        # Bullet-resistant glass partitions
        cv2.rectangle(frame, (30, int(height*0.22)), (200, int(height*0.45)), (190, 210, 205), 2)
        cv2.rectangle(frame, (230, int(height*0.22)), (400, int(height*0.45)), (190, 210, 205), 2)
        cv2.putText(frame, "TELLER 01", (60, int(height*0.42)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (120, 140, 140), 1)
        cv2.putText(frame, "TELLER 02", (260, int(height*0.42)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (120, 140, 140), 1)

        # ATM Kiosk on Right
        cv2.rectangle(frame, (width - 240, int(height*0.25)), (width - 120, int(height*0.75)), (55, 60, 65), -1)
        cv2.rectangle(frame, (width - 225, int(height*0.30)), (width - 135, int(height*0.45)), (160, 100, 40), -1) # ATM screen
        cv2.putText(frame, "24H ATM", (width - 215, int(height*0.28)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 229, 255), 1)

        # Vault corridor door in center background
        cv2.rectangle(frame, (int(width*0.48), int(height*0.22)), (int(width*0.62), int(height*0.55)), (70, 75, 85), -1)
        cv2.putText(frame, "SECURE ACCESS", (int(width*0.49), int(height*0.20)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (80, 80, 200), 1)

        # Security barrier stanchions with velvet ropes
        for sx in [480, 680, 880]:
            cv2.line(frame, (sx, int(height*0.52)), (sx, int(height*0.68)), (40, 160, 210), 3) # gold pole
            cv2.circle(frame, (sx, int(height*0.52)), 6, (40, 160, 210), -1)
        cv2.line(frame, (480, int(height*0.56)), (680, int(height*0.58)), (20, 20, 160), 2)
        cv2.line(frame, (680, int(height*0.58)), (880, int(height*0.56)), (20, 20, 160), 2)

        # Movement animation of suspect
        # Timeline:
        # 0.0 - 0.25: Enter from entrance (X: 1050 -> 480, Y: 430)
        # 0.25 - 0.50: Roam/Loiter near Teller 02 and Vault barrier (X: 480 -> 450 -> 540)
        # 0.50 - 0.75: Roam towards ATM kiosk and dwell (X: 540 -> 920 -> 880)
        # 0.75 - 1.00: Turn towards exit and leave frame (X: 880 -> 1180)
        
        t = f / total_frames
        
        if t < 0.25:
            phase = "ENTRY DETECTED"
            p = t / 0.25
            px = int(1050 - p * 580)
            py = int(height * 0.46 + p * 20)
            status_text = "ENTERED MAIN LOBBY"
        elif t < 0.50:
            phase = "LOITERING / RECONNAISSANCE"
            p = (t - 0.25) / 0.25
            px = int(470 + np.sin(p * 3.14 * 2) * 50)
            py = int(height * 0.48 + p * 15)
            status_text = "DWELLING NEAR TELLER COUNTER"
        elif t < 0.75:
            phase = "SUSPICIOUS ACTIVITY"
            p = (t - 0.50) / 0.25
            px = int(470 + p * 420 + np.sin(p * 3.14) * 30)
            py = int(height * 0.49 - np.sin(p * 3.14) * 20)
            status_text = "PROBING ATM & VAULT ACCESS"
        else:
            phase = "EXITING PREMISES"
            p = (t - 0.75) / 0.25
            px = int(890 + p * 320)
            py = int(height * 0.47 - p * 10)
            status_text = "RAPID EXIT VIA LOBBY DOORS"

        pw, ph = 70, 165
        
        # Draw suspect body:
        # Olive green utility jacket, dark trousers, dark blue cap, black face cover
        leg_step = int(np.sin(f * 0.8) * 14) if (t < 0.25 or t > 0.70 or (0.50 <= t <= 0.70)) else 0
        
        # Legs / Pants (Dark Navy)
        cv2.line(frame, (px + 24, py + ph - 35), (px + 15 + leg_step, py + ph), (30, 25, 25), 9)
        cv2.line(frame, (px + 46, py + ph - 35), (px + 55 - leg_step, py + ph), (30, 25, 25), 9)
        
        # Olive green utility jacket body
        cv2.rectangle(frame, (px + 12, py + 42), (px + 58, py + ph - 30), (45, 75, 60), -1) # Olive green (BGR: 45, 75, 60)
        # Jacket pockets / zipper
        cv2.line(frame, (px + 35, py + 42), (px + 35, py + ph - 30), (30, 50, 40), 2)
        cv2.rectangle(frame, (px + 16, py + 55), (px + 30, py + 72), (38, 65, 52), -1)
        cv2.rectangle(frame, (px + 40, py + 55), (px + 54, py + 72), (38, 65, 52), -1)
        
        # Crossbody bag strap
        cv2.line(frame, (px + 20, py + 44), (px + 52, py + 95), (60, 90, 120), 3)

        # Neck gaiter / black mask
        cv2.rectangle(frame, (px + 24, py + 26), (px + 46, py + 42), (20, 20, 22), -1)

        # Head & Cap (Navy Blue)
        cv2.circle(frame, (px + 35, py + 22), 16, (60, 45, 30), -1) # Navy cap
        cv2.ellipse(frame, (px + 32, py + 18), (18, 6), 10, 0, 360, (50, 35, 20), -1) # Cap visor
        
        # Neural Object Detection Bounding Box
        box_color = (0, 229, 255) if t < 0.50 else (0, 70, 255) # Yellow-cyan to Red alert
        cv2.rectangle(frame, (px, py), (px + pw, py + ph), box_color, 2)
        
        # Label HUD above box
        cv2.rectangle(frame, (px - 2, py - 24), (px + pw + 80, py), (10, 15, 20), -1)
        cv2.putText(frame, "POI #09 [0.95]", (px + 2, py - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, box_color, 1, cv2.LINE_AA)
        
        # Status pill below box
        cv2.rectangle(frame, (px - 2, py + ph), (px + pw + 110, py + ph + 20), (10, 15, 20), -1)
        cv2.putText(frame, f"{phase} | MASKED", (px + 2, py + ph + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 255, 180), 1, cv2.LINE_AA)

        # CCTV Visual Artifacts & Camera Grid
        # Subtle noise
        noise = np.random.randint(-5, 5, frame.shape, dtype=np.int16)
        frame = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        # Scanlines
        frame[::4, :, :] = (frame[::4, :, :] * 0.92).astype(np.uint8)

        # Top Left CCTV Header
        cv2.circle(frame, (35, 35), 7, (0, 0, 255), -1)
        cv2.putText(frame, "REC  [LIVE-STREAM]", (50, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "CAM 04 - METROPOLITAN BANK MAIN LOBBY & TELLER HALL", (35, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 229, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "1080P FORENSIC STREAM | PTZ AUTO-TRACKING ENABLED", (35, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 170, 180), 1, cv2.LINE_AA)

        # Top Right Timestamp
        sec_elapsed = f / fps
        time_str = f"2026-09-08 14:22:{int(10 + sec_elapsed):02d}.{int((sec_elapsed % 1) * 100):02d} UTC"
        cv2.putText(frame, time_str, (width - 450, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "AI PERSISTENT TRACK ID: TRK-BNK-09", (width - 450, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 229, 255), 1, cv2.LINE_AA)

        # Bottom Bar Status
        cv2.rectangle(frame, (0, height - 35), (width, height), (15, 18, 22), -1)
        cv2.putText(frame, f"SURVEILLANCE STATUS: {status_text} | SECTOR: BANK BRANCH 04 | BIOMETRIC: FACE MASKED (ALTERNATIVE GAIT ACTIVE)",
                    (25, height - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (100, 220, 200), 1, cv2.LINE_AA)

        out.write(frame)

    out.release()
    
    # Also duplicate to cam_bank_lobby.mp4 and processed evidence clip
    shutil.copy(output_path, output_path_alt)
    shutil.copy(output_path, output_clip_path)

    # Sync to backend/uploads and backend/processed
    shutil.copy(output_path, os.path.join(base_dir, "backend", "uploads", "videos", "bank_cctv_roaming_suspect.mp4"))
    shutil.copy(output_path, os.path.join(base_dir, "backend", "uploads", "videos", "cam_bank_lobby.mp4"))
    shutil.copy(output_clip_path, os.path.join(base_dir, "backend", "processed", "clips", "Bank_Reconnaissance_Suspect_Evidence.mp4"))
    
    if os.path.exists(suspect_img_path):
        shutil.copy(suspect_img_path, os.path.join(base_dir, "backend", "uploads", "images", "bank_suspect_reference.jpg"))
        shutil.copy(suspect_img_path, os.path.join(base_dir, "backend", "uploads", "images", "suspect_bank_loitering.jpg"))

    print("Bank CCTV video and suspect assets created successfully!")

if __name__ == "__main__":
    generate_bank_cctv_video()
