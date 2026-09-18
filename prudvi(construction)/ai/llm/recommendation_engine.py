"""
AI Recommendation Engine for BuildVerse AI.
Generates comprehensive site recovery strategies, material suggestions, and priority tasks.
"""

from typing import Dict, Any
from utils.helpers import calculate_date_offset

def generate_ai_recommendations(
    status: str,
    phase_name: str,
    delay_pct: float,
    current_completion_date: str = "2026-12-31"
) -> Dict[str, Any]:
    """Generates structured AI recommendations based on progress evaluation status."""
    if status == "On Schedule":
        return {
            "status": "Green",
            "message": "Construction is progressing as planned.",
            "is_on_schedule": True,
            "delay_reason": None,
            "missing_work": "None",
            "estimated_delay_days": 0,
            "extra_labour_required": "None",
            "material_suggestions": "Continue standard procurement rate.",
            "recovery_plan": "Maintain current shift schedule and worker velocity.",
            "new_completion_date": current_completion_date,
            "priority_tasks": [
                f"Complete final quality checks on {phase_name}",
                "Prepare raw material staging for next phase",
                "Perform standard safety audit"
            ]
        }
    else:
        delay_days = int(max(3, delay_pct * 1.8))
        extra_workers = max(2, int(delay_pct * 0.4))
        new_date = calculate_date_offset(current_completion_date, delay_days)
        
        return {
            "status": "Red" if delay_pct > 10.0 else "Orange",
            "message": f"Delay detected in {phase_name}. Immediate action required to stay on target.",
            "is_on_schedule": False,
            "delay_reason": f"Slower labor output and material supply bottleneck in {phase_name}.",
            "missing_work": f"{delay_pct:.1f}% remaining uncompleted structural section in {phase_name}.",
            "estimated_delay": f"{delay_days} Days",
            "estimated_delay_days": delay_days,
            "extra_labour_required": f"+{extra_workers} Skilled Masons / Workers on extended shift",
            "material_suggestions": "Procure rapid-setting cement additives and pre-mixed mortar bags to accelerate curing.",
            "recovery_plan": f"Deploy +{extra_workers} additional workers on evening shifts. Parallelize non-dependent task queues.",
            "new_completion_date": new_date,
            "priority_tasks": [
                f"Deploy overtime shift for {phase_name} completion",
                "Accelerate material supplier dispatch",
                "Re-align downstream phase dependencies in Gantt chart"
            ]
        }
