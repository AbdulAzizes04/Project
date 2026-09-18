"""
AI Construction Scheduler for BuildVerse AI.
Generates complete 12-phase project schedule with timelines, costs, labor, and materials.
"""

from typing import List, Dict, Any
from config import CONSTRUCTION_PHASES
from ai.construction.cost_estimator import estimate_phase_costs
from ai.construction.timeline_generator import generate_phase_timeline
from ai.construction.material_estimator import estimate_materials

DEPENDENCY_MAP = {
    "Foundation": [],
    "Columns": ["Foundation"],
    "Beams": ["Columns"],
    "Slab": ["Beams"],
    "Brick Work": ["Slab"],
    "Plastering": ["Brick Work"],
    "Electrical": ["Plastering"],
    "Plumbing": ["Plastering"],
    "Flooring": ["Electrical", "Plumbing"],
    "Painting": ["Flooring"],
    "Interior": ["Painting"],
    "Finishing": ["Interior"]
}

LABOR_MAP = {
    "Foundation": {"Masons": 6, "Helpers": 10},
    "Columns": {"Masons": 5, "Carpenters": 4, "Steel Fixers": 4},
    "Beams": {"Masons": 5, "Carpenters": 5, "Steel Fixers": 4},
    "Slab": {"Masons": 8, "Carpenters": 6, "Steel Fixers": 6},
    "Brick Work": {"Masons": 8, "Helpers": 8},
    "Plastering": {"Plasterers": 6, "Helpers": 6},
    "Electrical": {"Electricians": 4, "Helpers": 2},
    "Plumbing": {"Plumbers": 4, "Helpers": 2},
    "Flooring": {"Tile Masons": 5, "Helpers": 4},
    "Painting": {"Painters": 6, "Helpers": 3},
    "Interior": {"Carpenters": 6, "Designers": 2},
    "Finishing": {"Painters": 3, "Cleaners": 4}
}

def generate_full_construction_schedule(
    project_id: int,
    total_sqft: float,
    num_floors: int,
    total_budget: float,
    start_date: str,
    desired_completion_date: str,
    workers_available: int = 10,
    working_hours_per_day: float = 8.0
) -> List[Dict[str, Any]]:
    """Generates complete AI construction schedule array for database storage and Gantt chart display."""
    cost_breakdown = estimate_phase_costs(total_budget)
    materials = estimate_materials(total_sqft, num_floors)
    weights = [p["weight"] for p in CONSTRUCTION_PHASES]
    timelines = generate_phase_timeline(start_date, desired_completion_date, weights)
    
    schedules = []
    
    for i, phase in enumerate(CONSTRUCTION_PHASES):
        pname = phase["name"]
        cost_info = cost_breakdown[i]
        t_info = timelines[i]
        
        # Adjust labor based on available workers
        labor_count = min(workers_available, sum(LABOR_MAP.get(pname, {"Workers": 5}).values()))
        
        # Sample material requirement string for phase
        mat_str = f"Cement: {int(materials['cement_bags']*phase['weight'])} bags, Steel: {round(materials['steel_tons']*phase['weight'],1)} tons"
        
        schedules.append({
            "project_id": project_id,
            "phase_name": pname,
            "start_date": t_info["start_date"],
            "end_date": t_info["end_date"],
            "duration_days": t_info["duration_days"],
            "progress_pct": 0.0,
            "cost": cost_info["estimated_cost"],
            "labor": labor_count,
            "materials": mat_str,
            "dependencies": DEPENDENCY_MAP.get(pname, []),
            "status": "Pending"
        })
        
    return schedules
