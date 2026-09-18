"""
Timeline Generator module for calculating phase dates and calendar schedules.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any

def generate_phase_timeline(
    start_date_str: str,
    desired_end_date_str: str,
    phase_weights: List[float]
) -> List[Dict[str, str]]:
    """Calculates start and end dates for each phase based on available timeframe."""
    try:
        s_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        e_date = datetime.strptime(desired_end_date_str, "%Y-%m-%d")
        total_days = max(30, (e_date - s_date).days)
    except Exception:
        s_date = datetime.now()
        total_days = 180
        
    curr_date = s_date
    timelines = []
    
    for weight in phase_weights:
        duration = max(3, int(round(total_days * weight)))
        phase_start = curr_date
        phase_end = curr_date + timedelta(days=duration)
        
        timelines.append({
            "start_date": phase_start.strftime("%Y-%m-%d"),
            "end_date": phase_end.strftime("%Y-%m-%d"),
            "duration_days": duration
        })
        
        curr_date = phase_end + timedelta(days=1)
        
    return timelines
