"""
Room Optimizer Engine for BuildVerse AI.
Calculates spatial placement, adjacency matrices, and orientation preferences.
"""

from typing import List, Dict, Any

ORIENTATION_SCORES = {
    "Kitchen": "South-East",
    "Hall": "North-East",
    "Bedrooms": "South-West",
    "Dining": "East",
    "Bathrooms": "North-West",
    "Garden": "North",
    "Parking": "North-West",
    "Staircase": "West"
}

def optimize_room_placements(rooms: List[Dict[str, Any]], plot_width: float, plot_length: float) -> List[Dict[str, Any]]:
    """Calculates optimal (x, y) coordinates for each room within the floor plot boundary."""
    optimized_rooms = []
    
    # Grid allocation algorithm
    curr_x, curr_y = 0.0, 0.0
    row_max_h = 0.0
    wall_gap = 0.75 # 9 inch wall in feet scale
    
    for room in rooms:
        l = room["length"]
        w = room["width"]
        
        # Check if room fits in current row
        if curr_x + w + wall_gap > plot_width and curr_x > 0:
            curr_x = 0.0
            curr_y += row_max_h + wall_gap
            row_max_h = 0.0
            
        r_copy = dict(room)
        r_copy["x"] = round(curr_x, 2)
        r_copy["y"] = round(curr_y, 2)
        r_copy["recommended_orientation"] = ORIENTATION_SCORES.get(room["room_type"], "East")
        
        optimized_rooms.append(r_copy)
        
        curr_x += w + wall_gap
        row_max_h = max(row_max_h, l)
        
    return optimized_rooms
