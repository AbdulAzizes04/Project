"""
Digital Twin Sync Engine for updating 3D model element statuses from daily progress uploads.
"""

from typing import List, Dict, Any

def sync_twin_with_progress(project_id: int, current_progress_pct: float) -> List[Dict[str, Any]]:
    """Automatically updates Digital Twin 3D element statuses based on site completion %."""
    elements = [
        {"element_name": "Foundation Slab", "phase": "Foundation", "box": [0, 0, 0, 40, 50, 2], "threshold": 10.0},
        {"element_name": "Ground Columns", "phase": "Columns", "box": [2, 2, 2, 36, 46, 10], "threshold": 25.0},
        {"element_name": "Ground Beams & Slab", "phase": "Slab", "box": [0, 0, 12, 40, 50, 2], "threshold": 40.0},
        {"element_name": "Brick Walls Ground", "phase": "Brick Work", "box": [0, 0, 14, 40, 50, 10], "threshold": 60.0},
        {"element_name": "Plastering & Wiring", "phase": "Plastering", "box": [0.5, 0.5, 14.5, 39, 49, 9], "threshold": 75.0},
        {"element_name": "Roof & Finishing", "phase": "Finishing", "box": [0, 0, 24, 40, 50, 4], "threshold": 95.0}
    ]
    
    updated_elements = []
    for elem in elements:
        thresh = elem["threshold"]
        if current_progress_pct >= thresh:
            status = "Completed"
        elif current_progress_pct >= thresh - 15.0:
            status = "In-Progress"
        else:
            status = "Pending"
            
        e_copy = dict(elem)
        e_copy["status"] = status
        updated_elements.append(e_copy)
        
    return updated_elements
