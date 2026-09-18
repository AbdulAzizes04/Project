"""
Monitoring API module for BuildVerse AI.
"""

from typing import Dict, Any, List
from ai.vision.progress_detector import analyze_batch_media_session

def process_batch_monitoring_upload(
    file_paths: List[str],
    selected_area: str = "Ground Floor",
    selected_zone: str = "Balcony",
    building_block: str = "Block A"
) -> Dict[str, Any]:
    """Processes batch upload session (multiple images/videos) and returns Virtual Site Engineer report."""
    return analyze_batch_media_session(file_paths, selected_area, selected_zone, building_block)

def process_monitoring_upload(
    media_path: str,
    media_type: str = "images",
    planned_pct: float = 45.0,
    current_phase: str = "Brick Work",
    selected_floor: str = "Ground Floor",
    selected_block: str = "Block A"
) -> Dict[str, Any]:
    """Single upload alias mapping to Virtual Site Engineer analysis."""
    return analyze_batch_media_session([media_path], selected_floor, current_phase, selected_block)
