import os
import cv2
import numpy as np
import shutil

def build_bank_video():
    brain_dir = r"C:\Users\shaik\.gemini\antigravity-ide\brain\9b16d68e-be5f-40b4-9955-39544cf3a05e"
    workspace_dir = r"d:\projects\vision trace(supreethi)"
    
    bg_path = os.path.join(brain_dir, "bank_interior_cctv_1788919889756.jpg")
    suspect_path = os.path.join(brain_dir, "bank_suspect_fullbody_1788919910519.jpg")
    portrait_path = os.path.join(brain_dir, "bank_suspect_portrait_1788919870132.jpg")

    bg_img = cv2.imread(bg_path)
    suspect_img = cv2.imread(suspect_path)
    portrait_img = cv2.imread(portrait_path)

    if bg_img is None or suspect_img is None:
        raise ValueError("Could not load background or suspect image!")

    # Video output resolution
    width, height = 1280, 720
    fps = 30
    bg_resized = cv2.resize(bg_img, (width, height))

    # Segment suspect cleanly with accurate alpha channel
    h_orig, w_orig, _ = suspect_img.shape
    gray = cv2.cvtColor(suspect_img, cv2.COLOR_BGR2GRAY)
    boots_y, _ = np.where(gray < 60)
    max_boot_y = int(np.max(boots_y))

    bg_color = np.median(np.vstack([suspect_img[:30, :30], suspect_img[:30, -30:]]), axis=(0, 1))
    dist = np.linalg.norm(suspect_img.astype(np.float32) - bg_color, axis=2)
    raw_mask = (dist > 28.0).astype(np.uint8)
    raw_mask[max_boot_y + 2:, :] = 0

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    raw_mask = cv2.morphologyEx(raw_mask, cv2.MORPH_CLOSE, kernel)

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(raw_mask)
    largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
    x_s, y_s, w_s, h_s, _ = stats[largest_label]

    # Crop tightly around suspect
    crop_suspect = suspect_img[y_s:y_s+h_s, x_s:x_s+w_s]
    crop_mask = (labels[y_s:y_s+h_s, x_s:x_s+w_s] == largest_label).astype(np.float32)
    crop_mask = cv2.GaussianBlur(crop_mask, (5, 5), 0)

    # Save suspect reference images to project
    dest_uploads_img = os.path.join(workspace_dir, "uploads", "images")
    dest_proc_frames = os.path.join(workspace_dir, "processed", "frames")
    dest_public_img = os.path.join(workspace_dir, "frontend", "public", "images")
    os.makedirs(dest_uploads_img, exist_ok=True)
    os.makedirs(dest_proc_frames, exist_ok=True)
    os.makedirs(dest_public_img, exist_ok=True)

    cv2.imwrite(os.path.join(dest_uploads_img, "bank_suspect_portrait.jpg"), portrait_img)
    cv2.imwrite(os.path.join(dest_uploads_img, "suspect_reference_photo.jpg"), portrait_img)
    cv2.imwrite(os.path.join(dest_uploads_img, "suspect_candidate_07_masked.jpg"), portrait_img)
    cv2.imwrite(os.path.join(dest_proc_frames, "crop_poi_CASE-2026-089_track_7.jpg"), portrait_img)
    cv2.imwrite(os.path.join(dest_proc_frames, "bank_suspect_mugshot.jpg"), portrait_img)
    cv2.imwrite(os.path.join(dest_public_img, "bank_suspect_portrait.jpg"), portrait_img)
    cv2.imwrite(os.path.join(dest_public_img, "bank_suspect_fullbody.jpg"), suspect_img)
    print("Suspect portrait & fullbody reference photos updated.")

    # Define Trajectory Keypoints:
    # 1 person enters bank, roams the entire bank (lobby -> tellers -> vault & ATM -> lobby center), and leaves
    keyframes = [
        # 1. Entering through doors on left
        (0.00, -0.05, 0.68, "Entering bank doors"),
        (0.06,  0.08, 0.69, "Passes entrance threshold"),
        (0.12,  0.20, 0.72, "Enters main bank lobby"),
        # 2. Roaming past queue stanchions towards tellers
        (0.20,  0.36, 0.76, "Navigating around velvet stanchions"),
        (0.28,  0.55, 0.74, "Approaching bank teller stations"),
        (0.35,  0.72, 0.70, "Near Teller Window #2"),
        # 3. Pacing / Inspecting Teller counters
        (0.42,  0.84, 0.65, "Inspects Teller Window #4 cash drawer"),
        (0.48,  0.80, 0.62, "Scans teller counter partition glass"),
        # 4. Roaming to the back corridor / Vault & ATM area
        (0.56,  0.64, 0.52, "Walking into vault corridor"),
        (0.64,  0.54, 0.44, "Approaching 24HR ATM & Heavy Vault Door"),
        (0.70,  0.50, 0.43, "Loitering suspiciously at vault access"),
        # 5. Turning back and roaming through lobby center
        (0.78,  0.42, 0.56, "Pacing back through open lobby"),
        (0.85,  0.30, 0.66, "Moving towards bank exit"),
        # 6. Exiting through entrance glass doors
        (0.92,  0.16, 0.68, "Approaching glass double exit doors"),
        (0.97,  0.05, 0.68, "Pushes open exit door"),
        (1.00, -0.06, 0.68, "Left the bank premises")
    ]

    total_frames = 630  # 21 seconds @ 30fps

    def get_pos(progress):
        for i in range(len(keyframes) - 1):
            t0, x0, y0, _ = keyframes[i]
            t1, x1, y1, _ = keyframes[i+1]
            if t0 <= progress <= t1:
                local_t = (progress - t0) / (t1 - t0)
                s = (1.0 - np.cos(local_t * np.pi)) / 2.0
                x = x0 + s * (x1 - x0)
                y = y0 + s * (y1 - y0)
                dx = x1 - x0
                return x, y, dx
        return keyframes[-1][1], keyframes[-1][2], 0

    dest_uploads_vid = os.path.join(workspace_dir, "uploads", "videos")
    dest_proc_clips = os.path.join(workspace_dir, "processed", "clips")
    dest_public_vid = os.path.join(workspace_dir, "frontend", "public", "videos")
    os.makedirs(dest_uploads_vid, exist_ok=True)
    os.makedirs(dest_proc_clips, exist_ok=True)
    os.makedirs(dest_public_vid, exist_ok=True)

    out_raw_path = os.path.join(dest_uploads_vid, "bank_suspect_roaming.mp4")
    out_hud_path = os.path.join(dest_proc_clips, "bank_suspect_evidence.mp4")
    out_poi_path = os.path.join(dest_proc_clips, "Person_Of_Interest_07_Evidence.mp4")
    out_public_path = os.path.join(dest_public_vid, "bank_suspect_roaming.mp4")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer_raw = cv2.VideoWriter(out_raw_path, fourcc, fps, (width, height))
    writer_hud = cv2.VideoWriter(out_hud_path, fourcc, fps, (width, height))

    trajectory_history = []

    print(f"Rendering {total_frames} clean frames of bank surveillance simulation...")

    for f in range(total_frames):
        progress = f / float(total_frames - 1)
        rx, ry, dx = get_pos(progress)

        px = int(rx * width)
        py = int(ry * height)

        # 3D perspective scale calculation
        scale = 0.15 + (ry - 0.40) * 0.72
        scale = max(0.14, min(0.48, scale))

        target_h = int(height * scale)
        target_w = int(crop_suspect.shape[1] * (target_h / crop_suspect.shape[0]))

        bob = int(np.sin(f * 0.45) * 3.5)
        py_draw = py + bob

        facing_left = (dx < 0)
        current_crop = crop_suspect
        current_mask = crop_mask
        if facing_left:
            current_crop = cv2.flip(current_crop, 1)
            current_mask = cv2.flip(current_mask, 1)

        resized_suspect = cv2.resize(current_crop, (target_w, target_h), interpolation=cv2.INTER_AREA)
        resized_mask = cv2.resize(current_mask, (target_w, target_h), interpolation=cv2.INTER_LINEAR)

        frame_raw = bg_resized.copy()

        x_left = px - target_w // 2
        y_top = py_draw - target_h
        x_right = x_left + target_w
        y_bottom = py_draw

        foot_x = px
        foot_y = py_draw

        if x_right > 0 and x_left < width and y_bottom > 0 and y_top < height:
            # Contact floor shadow
            shadow_w = int(target_w * 0.65)
            shadow_h = int(target_h * 0.07)
            shadow_center = (foot_x, foot_y - 1)
            overlay_shadow = frame_raw.copy()
            cv2.ellipse(overlay_shadow, shadow_center, (shadow_w // 2, shadow_h // 2), 0, 0, 360, (10, 10, 15), -1)
            cv2.addWeighted(overlay_shadow, 0.45, frame_raw, 0.55, 0, frame_raw)

            # Alpha blend suspect
            sx1 = max(0, -x_left)
            sy1 = max(0, -y_top)
            sx2 = target_w - max(0, x_right - width)
            sy2 = target_h - max(0, y_bottom - height)

            dx1 = max(0, x_left)
            dy1 = max(0, y_top)
            dx2 = min(width, x_right)
            dy2 = min(height, y_bottom)

            if dx2 > dx1 and dy2 > dy1:
                alpha = resized_mask[sy1:sy2, sx1:sx2, np.newaxis]
                sub_fg = resized_suspect[sy1:sy2, sx1:sx2].astype(np.float32)
                sub_bg = frame_raw[dy1:dy2, dx1:dx2].astype(np.float32)
                blended = sub_fg * alpha + sub_bg * (1.0 - alpha)
                frame_raw[dy1:dy2, dx1:dx2] = np.clip(blended, 0, 255).astype(np.uint8)

            if f % 4 == 0 and x_left > 0 and x_right < width:
                trajectory_history.append((foot_x, foot_y))

        # CCTV grain / noise
        noise = np.random.randint(-4, 4, (height, width, 3), dtype=np.int16)
        frame_raw = np.clip(frame_raw.astype(np.int16) + noise, 0, 255).astype(np.uint8)

        # Subtle scanlines
        frame_raw[::4, :, :] = (frame_raw[::4, :, :] * 0.94).astype(np.uint8)

        frame_hud = frame_raw.copy()

        # Draw Trajectory on HUD
        if len(trajectory_history) > 1:
            for i in range(1, len(trajectory_history)):
                pt1 = trajectory_history[i-1]
                pt2 = trajectory_history[i]
                cv2.line(frame_hud, pt1, pt2, (0, 215, 255), 2, cv2.LINE_AA)
                if i % 3 == 0:
                    cv2.circle(frame_hud, pt2, 3, (0, 240, 255), -1)

        # Draw AI Bounding Box & HUD
        if x_right > 20 and x_left < width - 20 and y_bottom > 20:
            box_x1 = max(5, x_left - 4)
            box_y1 = max(5, y_top - 6)
            box_x2 = min(width - 5, x_right + 4)
            box_y2 = min(height - 5, y_bottom + 4)

            cyan = (0, 229, 255)
            cv2.rectangle(frame_hud, (box_x1, box_y1), (box_x2, box_y2), cyan, 2)
            c_len = 12
            cv2.line(frame_hud, (box_x1, box_y1), (box_x1 + c_len, box_y1), (255, 255, 255), 3)
            cv2.line(frame_hud, (box_x1, box_y1), (box_x1, box_y1 + c_len), (255, 255, 255), 3)
            cv2.line(frame_hud, (box_x2, box_y1), (box_x2 - c_len, box_y1), (255, 255, 255), 3)
            cv2.line(frame_hud, (box_x2, box_y1), (box_x2, box_y1 + c_len), (255, 255, 255), 3)
            cv2.line(frame_hud, (box_x1, box_y2), (box_x1 + c_len, box_y2), (255, 255, 255), 3)
            cv2.line(frame_hud, (box_x1, box_y2), (box_x1, box_y2 - c_len), (255, 255, 255), 3)
            cv2.line(frame_hud, (box_x2, box_y2), (box_x2 - c_len, box_y2), (255, 255, 255), 3)
            cv2.line(frame_hud, (box_x2, box_y2), (box_x2, box_y2 - c_len), (255, 255, 255), 3)

            cv2.rectangle(frame_hud, (box_x1, box_y1 - 22), (box_x1 + 175, box_y1), (15, 20, 25), -1)
            cv2.rectangle(frame_hud, (box_x1, box_y1 - 22), (box_x1 + 175, box_y1), cyan, 1)
            cv2.putText(frame_hud, "POI #07 [0.95] INTRUDER", (box_x1 + 6, box_y1 - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, cyan, 1, cv2.LINE_AA)

            cv2.rectangle(frame_hud, (box_x1, box_y2), (box_x1 + 195, box_y2 + 20), (15, 20, 25), -1)
            cv2.rectangle(frame_hud, (box_x1, box_y2), (box_x1 + 195, box_y2 + 20), (0, 100, 255), 1)
            cv2.putText(frame_hud, "GAIT-007 [92%] | MASKED", (box_x1 + 6, box_y2 + 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 220, 255), 1, cv2.LINE_AA)

        for f_img, is_hud in [(frame_raw, False), (frame_hud, True)]:
            rec_blink = ((f // 15) % 2 == 0)
            if rec_blink:
                cv2.circle(f_img, (35, 35), 8, (0, 0, 255), -1)
            else:
                cv2.circle(f_img, (35, 35), 8, (0, 0, 140), -1)

            cv2.putText(f_img, "REC  [LIVE-FEED]", (52, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(f_img, "CAM 04: FIRST METRO BANK - MAIN LOBBY & VAULT", (35, 72), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 229, 255), 2, cv2.LINE_AA)
            cv2.putText(f_img, "1080p @ 30.00 FPS | ENCRYPTED CCTV STREAM", (35, 96), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (190, 190, 190), 1, cv2.LINE_AA)

            sec_elapsed = f / float(fps)
            total_sec = 19 * 60 + 20 + sec_elapsed
            m = int(total_sec // 60)
            s = int(total_sec % 60)
            ms = int((sec_elapsed % 1.0) * 100)
            time_str = f"2026-09-08  23:{m:02d}:{s:02d}.{ms:02d} UTC"
            cv2.putText(f_img, time_str, (width - 440, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (255, 255, 255), 2, cv2.LINE_AA)
            hud_label = "AI FORENSIC RE-ID & TRAJECTORY ACTIVE" if is_hud else "RAW METROPOLITAN SURVEILLANCE FEED"
            cv2.putText(f_img, hud_label, (width - 440, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 229, 255), 1, cv2.LINE_AA)

            cv2.rectangle(f_img, (0, height - 32), (width, height), (8, 10, 14), -1)
            cv2.line(f_img, (0, height - 32), (width, height - 32), (30, 40, 50), 1)
            current_action = "PERSON ROAMING BANK"
            for k in keyframes:
                if progress >= k[0]:
                    current_action = k[3]
            footer_text = f"FRAME: {f:04d}/{total_frames} | STATUS: {current_action.upper()} | TARGET: SUSPECT #07 (MASKED)"
            cv2.putText(f_img, footer_text, (25, height - 11), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (120, 200, 170), 1, cv2.LINE_AA)

        writer_raw.write(frame_raw)
        writer_hud.write(frame_hud)

    writer_raw.release()
    writer_hud.release()

    shutil.copyfile(out_raw_path, out_public_path)
    shutil.copyfile(out_hud_path, out_poi_path)

    # Re-extract clean keyframes
    cap = cv2.VideoCapture(out_hud_path)
    frame_indices = [60, 180, 260, 420, 580]
    names = [
        'frame_01_suspect_entering_bank.jpg',
        'frame_02_suspect_lobby_counters.jpg',
        'frame_03_suspect_teller_inspection.jpg',
        'frame_04_suspect_vault_loitering.jpg',
        'frame_05_suspect_exiting_bank.jpg'
    ]
    for idx, name in zip(frame_indices, names):
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(os.path.join(brain_dir, name), frame)
            cv2.imwrite(os.path.join(dest_proc_frames, name), frame)
            cv2.imwrite(os.path.join(dest_public_img, name), frame)
    cap.release()

    print("Bank heist video generation complete with clean alpha segmentation!")

if __name__ == "__main__":
    build_bank_video()
