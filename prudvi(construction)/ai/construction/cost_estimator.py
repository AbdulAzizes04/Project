"""
Cost Estimator module for allocating project budget across construction phases.
"""

from typing import List, Dict, Any
from config import CONSTRUCTION_PHASES

def estimate_phase_costs(total_budget: float) -> List[Dict[str, Any]]:
    """Distributes total budget across standard construction phases based on cost weights."""
    allocated_phases = []
    
    for phase in CONSTRUCTION_PHASES:
        cost = round(total_budget * phase["weight"], 2)
        allocated_phases.append({
            "phase_name": phase["name"],
            "weight_pct": round(phase["weight"] * 100, 1),
            "estimated_cost": cost,
            "color": phase["color"]
        })
        
    return allocated_phases
