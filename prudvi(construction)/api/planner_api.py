"""
Planner API module for BuildVerse AI.
"""

from typing import List, Dict, Any
from ai.planner.floor_plan_ai import generate_2d_floor_plan, generate_3d_house_preview
from ai.planner.dimension_validator import validate_floor_plan

def process_floor_plan_request(plot_area: float, rooms: List[Dict[str, Any]]):
    """Processes floor plan request and validates architectural metrics."""
    validation = validate_floor_plan(plot_area, rooms)
    fig_2d = generate_2d_floor_plan(rooms, plot_width=40, plot_length=50)
    return {
        "validation": validation,
        "figure_2d": fig_2d
    }
