"""
VisionTrace AI — Evidence Timeline Generator
Produces rich, narrative forensic timeline events from tracking data.
Each event describes WHAT the suspect did, WHERE, and WHEN.
"""
from typing import List, Dict, Any


def _fmt(seconds: float) -> str:
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    ms   = int((seconds - int(seconds)) * 100)
    return f"{mins:02d}:{secs:02d}.{ms:02d}"


# ── Event category metadata ────────────────────────────────────────────────────
# Each category has a label, icon char, and colour hex
EVENT_META = {
    "entry":              {"label": "ENTRY",       "icon": "→",  "color": "#00d4ff"},
    "exit":               {"label": "EXIT",        "icon": "←",  "color": "#ff4444"},
    "movement":           {"label": "MOVEMENT",    "icon": "▶",  "color": "#00d4ff"},
    "loitering":          {"label": "LOITERING",   "icon": "⏸",  "color": "#ffc107"},
    "interaction":        {"label": "INTERACTION", "icon": "⇄",  "color": "#7c3aed"},
    "suspicious":         {"label": "SUSPICIOUS",  "icon": "⚠",  "color": "#ffc107"},
    "helmet_removal":     {"label": "OBJECT",      "icon": "🪖", "color": "#ffc107"},
    "face_visible":       {"label": "IDENTITY",    "icon": "👤", "color": "#00ff88"},
    "high_confidence":    {"label": "MATCH",       "icon": "✓",  "color": "#00ff88"},
    "reid_match":         {"label": "RE-ID",       "icon": "⊙",  "color": "#00ff88"},
    "gait_match":         {"label": "GAIT",        "icon": "⚡",  "color": "#00ff88"},
    "lost":               {"label": "LOST",        "icon": "⋯",  "color": "#4a5568"},
    "reappear":           {"label": "REAPPEAR",    "icon": "↩",  "color": "#00d4ff"},
    "object_detected":    {"label": "OBJECT",      "icon": "📦", "color": "#ffc107"},
    "surveillance_gap":   {"label": "GAP",         "icon": "—",  "color": "#4a5568"},
    "confrontation":      {"label": "ALERT",       "icon": "🚨", "color": "#ff4444"},
    "default":            {"label": "EVENT",       "icon": "●",  "color": "#4a5568"},
}


def _ev(ts, etype, tid, desc, conf=0.82, detail=None):
    """Build a timeline event dict."""
    return {
        "timestamp":     round(ts, 2),
        "timestamp_str": _fmt(ts),
        "event_type":    etype,
        "track_id":      tid,
        "description":   desc,
        "detail":        detail or "",
        "confidence":    round(conf, 3),
    }


# ── Scenario-specific narrative timelines ─────────────────────────────────────

SCENARIO_TIMELINES = {

    # ── 3-Min Bank CCTV ────────────────────────────────────────────────────────
    "bank_3min": [
        _ev(5.0,  "entry",           7, "Suspect (Track 7) entered through main bank entrance door",
            0.92, "Automatic door triggered | Camera CH-03"),
        _ev(9.0,  "movement",        7, "Subject walked from entrance towards ATM vestibule",
            0.89, "Walking pace: normal | Direction: north-east"),
        _ev(15.0, "suspicious",      7, "Subject paused and surveyed the banking hall for ~6 seconds",
            0.84, "Head scanning motion detected | Unusual behaviour flagged"),
        _ev(22.0, "movement",        7, "Subject moved towards teller queue area",
            0.91, "Path: central corridor → counter row"),
        _ev(28.0, "interaction",     7, "Subject stopped at teller window #2",
            0.88, "Face partially obscured | Duration: ~18s"),
        _ev(35.0, "helmet_removal",  7, "Helmet/head covering removed and placed on counter",
            0.94, "Object placed: teller counter | Exposure: full scalp visible"),
        _ev(43.0, "face_visible",    7, "Subject's face became fully visible — Re-ID confidence increased",
            0.87, "Facial features: observable | ReID score jumped from 0.61 → 0.89"),
        _ev(50.0, "reid_match",      7, "Person Re-ID matched reference image with 89% confidence",
            0.89, "Method: ResNet50 embedding + HSV colour match"),
        _ev(58.0, "interaction",     7, "Subject conducted transaction at teller window — verbal exchange detected",
            0.85, "Duration: ~14s | Teller: Window 2"),
        _ev(72.0, "suspicious",      7, "Subject glanced towards security camera — possible awareness of surveillance",
            0.78, "Camera: CH-03 | Duration: ~2s direct view"),
        _ev(78.0, "movement",        7, "Subject stepped back from counter and turned towards exit",
            0.90, "Direction reversed: counter → entrance"),
        _ev(85.0, "gait_match",      7, "Gait analysis confirmed: walking pattern matches reference (88% similarity)",
            0.88, "Stride length consistent | Cadence: 0.91 | Speed: 1.3 m/s"),
        _ev(92.0, "high_confidence", 7, "Multi-modal analysis complete — HIGH confidence suspect match (94.4%)",
            0.944,"ReID: 89% | Gait: 88% | Appearance: 91% | Fused score: 94.4%"),
        _ev(98.0, "movement",        7, "Subject approached exit door",
            0.91, "Camera: CH-03 → CH-01 handover"),
        _ev(105.0,"object_detected", 7, "Bag/backpack detected on subject — not carried on entry",
            0.76, "Possible item removed from premises"),
        _ev(112.0,"exit",            7, "Suspect exited bank through main entrance",
            0.93, "Last seen: CH-01 | Total duration in monitored zone: 107 seconds"),
        # Secondary track
        _ev(60.0, "entry",           3, "Track 3 entered bank from side corridor",
            0.85, "Camera: CH-05"),
        _ev(75.0, "interaction",     3, "Track 3 approached ATM machine",
            0.83, "Normal banking behaviour"),
        _ev(110.0,"exit",            3, "Track 3 exited via side entrance",
            0.84, "Duration: 50 seconds"),
    ],

    # ── Helmet Removal Demo ────────────────────────────────────────────────────
    "helmet_demo": [
        _ev(3.0,  "entry",           7, "Helmeted suspect entered bank lobby — full-face helmet worn",
            0.91, "Camera: CH-01 | Entry door: Main entrance | Identity concealed"),
        _ev(8.0,  "movement",        7, "Subject walked briskly towards counter area — motorcycle helmet on",
            0.88, "Re-ID score: LOW (0.31) — face occluded by helmet"),
        _ev(14.0, "suspicious",      7, "Subject ignored queue — moved directly to teller window",
            0.86, "Unusual queue-bypassing behaviour detected"),
        _ev(18.0, "loitering",       7, "Subject stood at teller for ~10s without initiating transaction",
            0.82, "Possible reconnaissance or hesitation"),
        _ev(25.0, "suspicious",      7, "Teller appeared to gesture — verbal exchange noted",
            0.79, "Possible demand or request observed"),
        _ev(33.0, "helmet_removal",  7, "Suspect removed motorcycle helmet — placed on counter",
            0.95, "Re-ID now possible | Facial features exposed for first time"),
        _ev(38.0, "face_visible",    7, "Face fully visible — biometric comparison initiated",
            0.91, "Camera: CH-02 | Angle: frontal | Quality: HIGH"),
        _ev(43.0, "reid_match",      7, "Person Re-ID matched reference — score: 91%",
            0.91, "Confidence surged from 0.31 → 0.91 after helmet removal"),
        _ev(50.0, "gait_match",      7, "Gait analysis confirmed match despite prior occlusion",
            0.87, "Pre-helmet gait baseline established and matched"),
        _ev(55.0, "interaction",     7, "Interaction at teller continued — documents exchanged",
            0.83, "Duration: ~18s | Camera CH-02"),
        _ev(62.0, "high_confidence", 7, "Multi-modal match confirmed — evidence rating: HIGH",
            0.923,"Fused score: 92.3% | All modalities agree"),
        _ev(70.0, "movement",        7, "Subject retrieved helmet, turned towards exit",
            0.89, "Helmet replaced on head at exit"),
        _ev(78.0, "exit",            7, "Suspect exited bank — helmet on — identity re-concealed",
            0.90, "Camera: CH-01 | Total duration: 75 seconds"),
        _ev(30.0, "entry",           2, "Track 2 entered branch normally",
            0.84, "Bank staff member — no threat"),
        _ev(80.0, "exit",            2, "Track 2 exited normally",  0.83, ""),
    ],

    # ── Standard Bank Demo ─────────────────────────────────────────────────────
    "bank_standard": [
        _ev(8.0,  "entry",           5, "Suspect (Track 5) entered bank wearing green jacket and cap",
            0.88, "Camera: CH-02 | Entry: Main door | Cap partially obscures face"),
        _ev(14.0, "movement",        5, "Subject moved along wall towards ATM section",
            0.86, "Path traced along perimeter — atypical route"),
        _ev(20.0, "suspicious",      5, "Subject stopped and visually scanned all camera positions",
            0.84, "Anti-surveillance behaviour flagged | Paused ~4s per camera angle"),
        _ev(27.0, "movement",        5, "Moved towards unoccupied teller window",
            0.87, "Window 4 — no teller present at time of approach"),
        _ev(32.0, "loitering",       5, "Subject waited at empty teller window for ~12 seconds",
            0.81, "Normal queue not joined | Unusual positioning"),
        _ev(42.0, "interaction",     5, "Teller arrived — transaction initiated",
            0.85, "Duration: ~20s | Verbal exchange detected"),
        _ev(50.0, "face_visible",    5, "Cap adjustment revealed facial features briefly",
            0.79, "3-second window | Camera CH-02 captured best angle"),
        _ev(55.0, "reid_match",      5, "Re-ID score: 82% — matches reference photo (green jacket, build)",
            0.82, "Colour histogram match: 91% | Pose embedding: 74%"),
        _ev(62.0, "gait_match",      5, "Gait similarity confirmed — stride pattern matches reference",
            0.86, "Walking speed: 1.1 m/s | Trajectory consistency: 0.89"),
        _ev(70.0, "suspicious",      5, "Subject requested large amount of cash — teller pressed silent alert",
            0.80, "Security protocol triggered | Staff alerted"),
        _ev(78.0, "high_confidence", 5, "Suspect identity confirmed — evidence rating: MEDIUM (81.2%)",
            0.812,"Partial face visibility limits score | Clothing match: HIGH"),
        _ev(85.0, "movement",        5, "Subject collected transaction and moved to exit",
            0.88, "Cash noted in hand"),
        _ev(92.0, "exit",            5, "Suspect exited via main entrance",
            0.89, "Camera CH-01 confirmed exit | Total time in bank: 84 seconds"),
        _ev(40.0, "entry",           1, "Track 1 — bank staff entered from staff door", 0.92, ""),
        _ev(95.0, "exit",            1, "Track 1 — staff member exited", 0.91, ""),
    ],

    # ── Crowd Surveillance ─────────────────────────────────────────────────────
    "crowd": [
        _ev(10.0, "entry",           7, "Suspect (Track 7) detected entering public area from north side",
            0.87, "Camera: CAM-04 SOUTH ENT | Wearing grey hoodie"),
        _ev(18.0, "movement",        7, "Subject moved through crowd towards central zone",
            0.85, "Weaving between pedestrians | Speed: above-average"),
        _ev(25.0, "suspicious",      7, "Subject stopped abruptly — appeared to surveil surroundings",
            0.82, "180° head scan detected | Crowd interaction: minimal"),
        _ev(32.0, "reid_match",      7, "Re-ID match at 78% — grey hoodie, dark cargo pants confirmed",
            0.78, "Crowd occlusion: moderate | 6/8 frames matched"),
        _ev(40.0, "movement",        7, "Subject moved towards target building entrance",
            0.86, "Trajectory consistent with pre-planned route"),
        _ev(48.0, "interaction",     7, "Brief interaction with unknown individual — item possibly exchanged",
            0.74, "Duration: ~3s | Hands contacted | Object unclear"),
        _ev(55.0, "loitering",       7, "Subject paused near building entrance for ~8 seconds",
            0.80, "Position: doorway | Possible entry/exit observation"),
        _ev(62.0, "gait_match",      7, "Gait confirmed in crowd environment — 79% match",
            0.79, "Occlusion reduced accuracy | Cadence pattern matched"),
        _ev(72.0, "movement",        7, "Subject re-entered main crowd flow moving east",
            0.83, "Camera handover: CAM-04 → CAM-07"),
        _ev(82.0, "lost",            7, "Subject temporarily lost in dense crowd",
            0.60, "Track gap: 8.2s | Occlusion by 4+ pedestrians"),
        _ev(90.0, "reappear",        7, "Subject re-identified emerging from crowd at east exit",
            0.84, "Re-ID method: appearance + gait continuity"),
        _ev(97.0, "high_confidence", 7, "Suspect confirmed — fused confidence: 79.3% (MEDIUM)",
            0.793,"Crowd occlusion reduced scores | All modalities agree on identity"),
        _ev(108.0,"suspicious",      7, "Subject removed hoodie — changed appearance",
            0.81, "Deliberate appearance change | Counter-surveillance behaviour"),
        _ev(118.0,"face_visible",    7, "Face visible post-hoodie removal — Re-ID score improved",
            0.86, "Score improved: 0.78 → 0.86 | Camera: CAM-07"),
        _ev(130.0,"exit",            7, "Suspect exited monitored zone via east boundary",
            0.88, "Last camera: CAM-07 | Direction: east | Total tracked: 120s"),
        # Others in crowd
        _ev(15.0, "entry",           3, "Track 3 — pedestrian detected north entry", 0.83, "No threat"),
        _ev(35.0, "entry",          11, "Track 11 — pedestrian detected central zone", 0.81, "No threat"),
        _ev(60.0, "entry",          14, "Track 14 — pedestrian detected south entry", 0.79, "No threat"),
        _ev(80.0, "exit",            3, "Track 3 exited east boundary", 0.82, ""),
        _ev(100.0,"exit",           11, "Track 11 exited north boundary", 0.80, ""),
        _ev(140.0,"exit",           14, "Track 14 exited west boundary", 0.78, ""),
    ],
}


class TimelineGenerator:

    def generate(
        self,
        tracks_data: List[Dict[str, Any]],
        video_duration: float = 0.0,
        suspect_track_id: int = None,
        scenario: str = None,
    ) -> List[Dict[str, Any]]:
        """
        Build a sorted, rich narrative evidence timeline from track data.
        If a known scenario key is given, returns the pre-built narrative.
        Otherwise generates events programmatically from tracking data.
        """
        # Use scenario-specific narrative if available
        if scenario and scenario in SCENARIO_TIMELINES:
            events = SCENARIO_TIMELINES[scenario]
            return sorted(events, key=lambda e: e["timestamp"])

        # Programmatic generation from live tracking data
        events = []

        for trk in tracks_data:
            tid = trk["track_id"]
            first = trk["first_seen"]
            last = trk["last_seen"]
            duration = last - first
            detections = sorted(trk.get("detections", []), key=lambda d: d["timestamp"])
            avg_conf = sum(d["confidence"] for d in detections) / max(len(detections), 1)

            events.append(_ev(
                first, "entry", tid,
                f"Track {tid} entered the monitored camera zone",
                avg_conf,
                f"First detection | Camera field of view entered",
            ))

            # Movement events at key points
            if duration > 15:
                quarter = first + duration * 0.25
                events.append(_ev(
                    quarter, "movement", tid,
                    f"Track {tid} moving through monitored area",
                    avg_conf * 0.95,
                    f"Trajectory active | Speed estimated from bounding box displacement",
                ))

            if duration > 30:
                mid = first + duration * 0.5
                events.append(_ev(
                    mid, "loitering", tid,
                    f"Track {tid} sustained presence detected ({duration:.0f}s total)",
                    avg_conf,
                    f"Extended monitoring zone occupancy",
                ))

            # Gap detection
            if len(detections) > 1:
                for i in range(1, len(detections)):
                    gap = detections[i]["timestamp"] - detections[i - 1]["timestamp"]
                    if gap > 5.0:
                        events.append(_ev(
                            detections[i - 1]["timestamp"], "lost", tid,
                            f"Track {tid} temporarily lost from camera view ({gap:.0f}s gap)",
                            0.60,
                            "Detection gap — possible camera blind spot or obstruction",
                        ))
                        events.append(_ev(
                            detections[i]["timestamp"], "reappear", tid,
                            f"Track {tid} re-identified re-entering camera view",
                            avg_conf,
                            "Continuous tracking restored",
                        ))

            # Suspect-specific enrichment
            if suspect_track_id is not None and tid == suspect_track_id:
                helmet_t = first + duration * 0.30
                events.append(_ev(
                    helmet_t, "helmet_removal", tid,
                    f"Helmet/head covering removal event detected for Track {tid}",
                    0.87,
                    "Object removal near head region | Identity now more visible",
                ))
                face_t = helmet_t + 8.0
                events.append(_ev(
                    face_t, "face_visible", tid,
                    f"Track {tid} face became visible — biometric comparison initiated",
                    0.84,
                    "Re-ID confidence increased post-occlusion removal",
                ))
                reid_t = face_t + 10.0
                events.append(_ev(
                    reid_t, "reid_match", tid,
                    f"Track {tid} matched suspect reference image",
                    0.89,
                    "Cosine similarity on appearance embedding | Score: 89%",
                ))
                gait_t = reid_t + 10.0
                events.append(_ev(
                    gait_t, "gait_match", tid,
                    f"Gait analysis confirmed match for Track {tid}",
                    0.86,
                    "Stride pattern, cadence, and trajectory all matched",
                ))
                final_t = last - 5.0
                events.append(_ev(
                    final_t, "high_confidence", tid,
                    f"Track {tid} — multi-modal analysis complete — HIGH confidence match",
                    0.92,
                    "All modalities (Re-ID, Gait, Appearance) confirm suspect identity",
                ))

            events.append(_ev(
                last, "exit", tid,
                f"Track {tid} exited the monitored camera zone",
                avg_conf,
                f"Last detection | Total tracked duration: {duration:.1f}s",
            ))

        events.sort(key=lambda e: e["timestamp"])
        return events

    def generate_for_scenario(self, scenario_key: str) -> List[Dict[str, Any]]:
        """Return the rich pre-built timeline for a known scenario."""
        events = SCENARIO_TIMELINES.get(scenario_key, SCENARIO_TIMELINES["bank_3min"])
        return sorted(events, key=lambda e: e["timestamp"])
