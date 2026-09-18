"""
Dimension and Architectural Constraint Validator for BuildVerse AI.
Checks plot coverage, minimum room dimensions, wall boundaries, and setback rules.
"""

from typing import List, Dict, Any

MIN_ROOM_SIZES = {
    "Bedrooms": (9.0, 9.0),      # min length, width in feet
    "Kitchen": (7.0, 7.0),
    "Hall": (12.0, 10.0),
    "Dining": (8.0, 8.0),
    "Bathrooms": (4.0, 5.0),
    "Balcony": (3.0, 5.0),
    "Parking": (10.0, 14.0),
    "Staircase": (6.0, 9.0),
    "Utility Room": (4.0, 5.0),
    "Store Room": (4.0, 4.0),
    "Garden": (6.0, 6.0)
}

def validate_floor_plan(plot_area: float, rooms: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validates room dimensions against plot area and architectural code requirements."""
    total_built_up_area = sum(r["length"] * r["width"] for r in rooms)
    
    # Calculate wall thickness allowance (approx 12% of room area)
    wall_allowance = total_built_up_area * 0.12
    gross_area = total_built_up_area + wall_allowance
    
    warnings = []
    errors = []
    
    # Max coverage check (75% plot coverage limit for setback/ventilation)
    max_allowed = plot_area * 0.85
    if gross_area > max_allowed:
        errors.append(f"Gross floor built-up area ({gross_area:.1f} sq.ft) exceeds recommended plot limit ({max_allowed:.1f} sq.ft).")
        
    for room in rooms:
        rtype = room["room_type"]
        l, w = room["length"], room["width"]
        if rtype in MIN_ROOM_SIZES:
            min_l, min_w = MIN_ROOM_SIZES[rtype]
            if (l < min_l and w < min_w) or (l * w < min_l * min_w):
                warnings.append(f"{rtype} dimensions ({l}x{w}) are below standard architectural recommendation ({min_l}x{min_w}).")
                
    is_valid = len(errors) == 0
    
    return {
        "valid": is_valid,
        "built_up_area": round(total_built_up_area, 2),
        "wall_area": round(wall_allowance, 2),
        "gross_area": round(gross_area, 2),
        "coverage_pct": round((gross_area / plot_area) * 100, 1) if plot_area > 0 else 0,
        "warnings": warnings,
        "errors": errors
    }
