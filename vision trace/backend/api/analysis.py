"""
VisionTrace AI — Analysis API
Handles file upload, pipeline execution, status polling, and demo scenarios.
"""
import os
import time
import random
import asyncio
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from database.database import get_db
from database import models, schemas
from services.video_processor import VideoProcessor
from services.person_detector import PersonDetector
from services.tracker import MultiTargetTracker
from services.person_reid import PersonReID
from services.gait_analysis import GaitAnalyzer
from services.similarity_fusion import SimilarityFusion
from services.timeline_generator import TimelineGenerator

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])

# Global status store (in-memory; fine for single-process demo)
_status_store: dict = {}

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "uploads")
VIDEO_DIR = os.path.join(UPLOAD_DIR, "videos")
REF_DIR = os.path.join(UPLOAD_DIR, "reference_images")
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(REF_DIR, exist_ok=True)


def _save_upload(file: UploadFile, directory: str) -> str:
    safe_name = file.filename.replace(" ", "_")
    path = os.path.join(directory, safe_name)
    with open(path, "wb") as f:
        f.write(file.file.read())
    return path


def _set_status(case_id: int, step: int, total: int, name: str, progress: float, msg: str):
    _status_store[case_id] = {
        "case_id": case_id,
        "status": "processing",
        "current_step": step,
        "total_steps": total,
        "step_name": name,
        "progress": progress,
        "message": msg,
    }


def _done_status(case_id: int):
    _status_store[case_id] = {
        "case_id": case_id,
        "status": "completed",
        "current_step": 7,
        "total_steps": 7,
        "step_name": "Complete",
        "progress": 1.0,
        "message": "Investigation completed successfully",
    }


@router.post("/upload")
async def upload_files(
    case_id: int = Form(...),
    video: Optional[UploadFile] = File(None),
    reference_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(404, "Case not found")

    if video:
        vpath = _save_upload(video, VIDEO_DIR)
        case.video_path = vpath
        case.video_name = video.filename

    if reference_image:
        rpath = _save_upload(reference_image, REF_DIR)
        case.reference_image_path = rpath

    db.commit()
    return {"message": "Files uploaded", "case_id": case_id}


@router.post("/run")
async def run_pipeline(
    req: schemas.AnalysisRunRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    case = db.query(models.Case).filter(models.Case.id == req.case_id).first()
    if not case:
        raise HTTPException(404, "Case not found")

    _set_status(req.case_id, 0, 7, "Initialising", 0.0, "Starting pipeline...")
    case.status = "processing"
    db.commit()

    if req.demo_mode:
        background_tasks.add_task(_run_demo_pipeline, req.case_id, req.demo_scenario, db)
    else:
        background_tasks.add_task(
            _run_real_pipeline,
            req.case_id,
            case.video_path,
            case.reference_image_path,
            req.similarity_threshold,
            req.fps,
            db,
        )

    return {"message": "Pipeline started", "case_id": req.case_id}


@router.get("/{case_id}/status", response_model=schemas.ProcessingStatus)
def get_status(case_id: int):
    if case_id not in _status_store:
        return schemas.ProcessingStatus(
            case_id=case_id, status="pending", current_step=0,
            total_steps=7, step_name="Waiting", progress=0.0, message="Not started",
        )
    s = _status_store[case_id]
    return schemas.ProcessingStatus(**s)


# ── Demo pipeline ──────────────────────────────────────────────────────────────

DEMO_SCENARIOS = {
    "bank_3min": {
        "name": "3-Min Bank CCTV Simulation",
        "total_frames": 360, "persons_tracked": 8, "matches_found": 5,
        "confidence": 0.944, "processing_time": 14.2, "evidence_rating": "HIGH",
    },
    "helmet_demo": {
        "name": "Helmet Removal CCTV Demo",
        "total_frames": 150, "persons_tracked": 4, "matches_found": 2,
        "confidence": 0.887, "processing_time": 7.8, "evidence_rating": "HIGH",
    },
    "bank_standard": {
        "name": "Standard Bank CCTV Demo",
        "total_frames": 240, "persons_tracked": 6, "matches_found": 3,
        "confidence": 0.812, "processing_time": 11.1, "evidence_rating": "MEDIUM",
    },
    "crowd": {
        "name": "4.5-Min Crowd Surveillance",
        "total_frames": 540, "persons_tracked": 16, "matches_found": 12,
        "confidence": 0.793, "processing_time": 21.5, "evidence_rating": "MEDIUM",
    },
}

STEPS = [
    "Extracting video frames",
    "Detecting persons",
    "Tracking individuals",
    "Person re-identification",
    "Gait analysis",
    "Multi-modal score fusion",
    "Generating forensic evidence timeline",
]


def _run_demo_pipeline(case_id: int, scenario_key: str, db: Session):
    scenario = DEMO_SCENARIOS.get(scenario_key, DEMO_SCENARIOS["bank_3min"])
    total = len(STEPS)

    for i, step in enumerate(STEPS):
        _set_status(case_id, i + 1, total, step, (i + 1) / total, f"Processing: {step}")
        time.sleep(random.uniform(0.8, 1.5))  # simulate work

    # Persist results
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        return

    case.total_frames = scenario["total_frames"]
    case.persons_tracked = scenario["persons_tracked"]
    case.matches_found = scenario["matches_found"]
    case.overall_confidence = scenario["confidence"]
    case.processing_time = scenario["processing_time"]
    case.evidence_rating = scenario["evidence_rating"]
    case.status = "completed"
    case.video_name = case.video_name or scenario["name"]
    db.commit()

    # Create tracks
    from services.gait_analysis import GaitAnalyzer
    from services.similarity_fusion import SimilarityFusion, classify_confidence
    from services.timeline_generator import TimelineGenerator

    gait_svc = GaitAnalyzer()
    fusion = SimilarityFusion()
    tl = TimelineGenerator()

    tracks_data = []
    for tn in range(1, scenario["persons_tracked"] + 1):
        rng = random.Random(tn * 7 + case_id)
        first = rng.uniform(5, 60)
        dur = rng.uniform(10, 120)
        last = first + dur
        appearances = int(dur * 2)
        avg_conf = rng.uniform(0.72, 0.96)

        track = models.Track(
            case_id=case_id,
            track_number=tn,
            first_seen=first,
            last_seen=last,
            duration=dur,
            avg_confidence=avg_conf,
            appearance_count=appearances,
        )
        db.add(track)
        db.flush()

        # Gait & ReID scores
        base = 0.88 if tn <= scenario["matches_found"] else 0.55
        gait_result = gait_svc.simulate_for_track(tn, base)
        reid_score = max(0.0, min(1.0, base + rng.uniform(-0.08, 0.08)))
        cloth_score = max(0.0, min(1.0, base + rng.uniform(-0.10, 0.06)))

        fusion_result = fusion.fuse(reid_score, gait_result["gait_similarity"], cloth_score)
        ar = models.AnalysisResult(
            case_id=case_id,
            track_id=track.id,
            reid_score=reid_score,
            gait_score=gait_result["gait_similarity"],
            clothing_score=cloth_score,
            face_score=0.0,
            final_score=fusion_result["final_score"],
            evidence_rating=fusion_result["evidence_rating"],
        )
        db.add(ar)

        # Add a few detections for timeline
        for step_i in range(min(5, appearances)):
            ts = first + (step_i / max(appearances - 1, 1)) * dur
            det = models.Detection(
                track_id=track.id,
                timestamp=round(ts, 2),
                frame_number=int(ts * 2),
                confidence=avg_conf,
                bounding_box=[100, 80, 220, 400],
            )
            db.add(det)

        tracks_data.append({
            "track_id": tn,
            "first_seen": first,
            "last_seen": last,
            "detections": [{"timestamp": first + i * dur / max(appearances, 1), "confidence": avg_conf}
                           for i in range(min(5, appearances))],
        })

    db.commit()

    # Generate timeline events
    suspect_tid = 7 if scenario["persons_tracked"] >= 7 else 1
    events = tl.generate(tracks_data, suspect_track_id=suspect_tid)
    for ev in events:
        e = models.Evidence(
            case_id=case_id,
            track_id=ev.get("track_id"),
            timestamp=ev["timestamp"],
            event_type=ev["event_type"],
            confidence=ev["confidence"],
            description=ev["description"],
        )
        db.add(e)
    db.commit()

    _done_status(case_id)


def _run_real_pipeline(
    case_id: int,
    video_path: str,
    ref_image_path: str,
    threshold: float,
    fps: int,
    db: Session,
):
    """Real AI pipeline — runs when files are available."""
    import cv2
    import numpy as np

    start_time = time.time()
    total = len(STEPS)

    try:
        # Step 1: Extract frames
        _set_status(case_id, 1, total, STEPS[0], 0.1, "Extracting frames...")
        vp = VideoProcessor(output_dir="temp_frames")

        if not video_path or not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")

        frames_data = vp.extract_frames(video_path, target_fps=fps)
        _set_status(case_id, 1, total, STEPS[0], 1.0, f"Extracted {len(frames_data)} frames")

        # Step 2: Detect persons
        _set_status(case_id, 2, total, STEPS[1], 0.1, "Running YOLO detection...")
        detector = PersonDetector()
        detected_frames = detector.detect_batch(frames_data)
        _set_status(case_id, 2, total, STEPS[1], 1.0, "Detection complete")

        # Step 3: Track
        _set_status(case_id, 3, total, STEPS[2], 0.1, "Tracking individuals...")
        tracker = MultiTargetTracker()
        all_tracks: dict = {}  # track_id → list of detection records

        for fd in detected_frames:
            tracked_dets = tracker.update(fd["detections"], fd.get("frame"))
            for det in tracked_dets:
                tid = det["track_id"]
                if tid not in all_tracks:
                    all_tracks[tid] = []
                all_tracks[tid].append({
                    "timestamp": fd["timestamp"],
                    "frame_number": fd["frame_number"],
                    "confidence": det["confidence"],
                    "bbox": det["bbox"],
                    "frame": fd.get("frame"),
                })

        _set_status(case_id, 3, total, STEPS[2], 1.0, f"Tracked {len(all_tracks)} individuals")

        # Load reference image
        ref_img = None
        if ref_image_path and os.path.exists(ref_image_path):
            ref_img = cv2.imread(ref_image_path)

        reid_svc = PersonReID()
        gait_svc = GaitAnalyzer()
        fusion = SimilarityFusion()

        # Step 4: ReID
        _set_status(case_id, 4, total, STEPS[3], 0.1, "Running Re-ID analysis...")
        reid_scores = {}
        for tid, dets in all_tracks.items():
            if ref_img is not None and dets:
                best_frame = dets[len(dets) // 2]
                frame = best_frame.get("frame")
                if frame is not None:
                    crop = vp.crop_person(frame, best_frame["bbox"])
                    scores = reid_svc.compare(ref_img, crop)
                else:
                    scores = reid_svc.compare_simulated(tid)
            else:
                scores = reid_svc.compare_simulated(tid)
            reid_scores[tid] = scores
        _set_status(case_id, 4, total, STEPS[3], 1.0, "Re-ID complete")

        # Step 5: Gait
        _set_status(case_id, 5, total, STEPS[4], 0.1, "Analysing gait patterns...")
        gait_scores = {}
        meta = vp.get_video_metadata(video_path)
        for tid, dets in all_tracks.items():
            gait_scores[tid] = gait_svc.analyze_track(dets, meta["fps"])
        _set_status(case_id, 5, total, STEPS[4], 1.0, "Gait analysis complete")

        # Step 6: Fusion
        _set_status(case_id, 6, total, STEPS[5], 0.1, "Fusing multi-modal scores...")
        fusion_results = {}
        for tid in all_tracks:
            r = reid_scores.get(tid, {})
            g = gait_scores.get(tid, {})
            fusion_results[tid] = fusion.fuse(
                r.get("reid_score", 0.5),
                g.get("gait_similarity", 0.5),
                r.get("clothing_score", 0.5),
            )
        _set_status(case_id, 6, total, STEPS[5], 1.0, "Score fusion complete")

        # Step 7: Save to DB + timeline
        _set_status(case_id, 7, total, STEPS[6], 0.1, "Generating evidence timeline...")
        case = db.query(models.Case).filter(models.Case.id == case_id).first()

        matches = sum(1 for f in fusion_results.values() if f["final_score"] >= threshold)
        avg_conf = sum(f["final_score"] for f in fusion_results.values()) / max(len(fusion_results), 1)
        best_rating = "LOW"
        for f in fusion_results.values():
            if f["evidence_rating"] == "HIGH":
                best_rating = "HIGH"
                break
            if f["evidence_rating"] == "MEDIUM":
                best_rating = "MEDIUM"

        case.total_frames = len(frames_data)
        case.persons_tracked = len(all_tracks)
        case.matches_found = matches
        case.overall_confidence = round(avg_conf, 4)
        case.processing_time = round(time.time() - start_time, 2)
        case.evidence_rating = best_rating
        case.status = "completed"
        db.commit()

        tracks_data_for_tl = []
        for tid, dets in all_tracks.items():
            first = min(d["timestamp"] for d in dets)
            last = max(d["timestamp"] for d in dets)
            track = models.Track(
                case_id=case_id,
                track_number=tid,
                first_seen=first,
                last_seen=last,
                duration=last - first,
                avg_confidence=sum(d["confidence"] for d in dets) / len(dets),
                appearance_count=len(dets),
            )
            db.add(track)
            db.flush()

            fr = fusion_results.get(tid, {})
            ar = models.AnalysisResult(
                case_id=case_id,
                track_id=track.id,
                reid_score=fr.get("reid_score", 0),
                gait_score=fr.get("gait_score", 0),
                clothing_score=fr.get("clothing_score", 0),
                face_score=fr.get("face_score", 0),
                final_score=fr.get("final_score", 0),
                evidence_rating=fr.get("evidence_rating", "LOW"),
            )
            db.add(ar)

            for det in dets[:10]:
                d = models.Detection(
                    track_id=track.id,
                    timestamp=det["timestamp"],
                    frame_number=det["frame_number"],
                    confidence=det["confidence"],
                    bounding_box=det["bbox"],
                )
                db.add(d)

            tracks_data_for_tl.append({
                "track_id": tid,
                "first_seen": first,
                "last_seen": last,
                "detections": dets,
            })

        db.commit()

        tl = TimelineGenerator()
        suspect_tid = max(fusion_results, key=lambda t: fusion_results[t]["final_score"], default=None)
        events = tl.generate(tracks_data_for_tl, suspect_track_id=suspect_tid)
        for ev in events:
            e = models.Evidence(
                case_id=case_id,
                track_id=ev.get("track_id"),
                timestamp=ev["timestamp"],
                event_type=ev["event_type"],
                confidence=ev["confidence"],
                description=ev["description"],
            )
            db.add(e)
        db.commit()

        _done_status(case_id)

    except Exception as ex:
        case = db.query(models.Case).filter(models.Case.id == case_id).first()
        if case:
            case.status = "error"
            db.commit()
        _status_store[case_id] = {
            "case_id": case_id, "status": "error",
            "current_step": 0, "total_steps": 7,
            "step_name": "Error", "progress": 0.0,
            "message": str(ex),
        }
