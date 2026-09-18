"""
Material Estimator for BuildVerse AI.
Calculates structural building material quantities based on floor built-up area.
"""

from typing import Dict, Any

def estimate_materials(total_sqft: float, num_floors: int = 1) -> Dict[str, Any]:
    """Estimates construction material requirements based on engineering benchmarks."""
    total_area = total_sqft * num_floors
    
    # Material consumption standards per sq.ft
    cement_bags = total_area * 0.40       # 0.4 bags per sq.ft
    steel_kg = total_area * 3.5           # 3.5 kg per sq.ft
    bricks = total_area * 18.0            # 18 bricks per sq.ft
    sand_tons = total_area * 0.055        # 0.055 tons per sq.ft
    aggregate_tons = total_area * 0.040   # 0.04 tons per sq.ft
    paint_liters = total_area * 0.18      # 0.18 liters per sq.ft
    flooring_tiles_sqft = total_area * 0.85 # 85% tile coverage
    
    return {
        "total_built_up_area": round(total_area, 2),
        "cement_bags": int(np_ceil(cement_bags)),
        "steel_tons": round(steel_kg / 1000.0, 2),
        "bricks_count": int(np_ceil(bricks)),
        "sand_tons": round(sand_tons, 1),
        "aggregate_tons": round(aggregate_tons, 1),
        "paint_liters": int(np_ceil(paint_liters)),
        "flooring_tiles_sqft": round(flooring_tiles_sqft, 1)
    }

def np_ceil(val):
    import math
    return math.ceil(val)
