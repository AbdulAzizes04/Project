import re
from typing import Dict, Any, List

class ForensicNLPSearchEngine:
    """
    Natural Language Query Parser for Surveillance Video Metadata.
    Extracts forensic query parameters:
    - Clothing color & attributes (black, red, hoodie, denim, jacket)
    - Temporal constraints (after 7 PM, before 8:30 PM, between 07:00 and 08:00)
    - Camera / Spatial filter (Camera 1, Camera 2, Entrance, Vault, Parking)
    - Object category (person, vehicle, car, suspect, masked)
    - Gait / Velocity terms (running, fast walking, limping, slow)
    """
    def parse_query(self, query: str) -> Dict[str, Any]:
        q_lower = query.lower()
        filters = {
            "raw_query": query,
            "target_type": "all",
            "colors": [],
            "camera": None,
            "time_after": None,
            "time_before": None,
            "is_masked": None,
            "gait_speed": None,
            "keywords": []
        }

        # Target type
        if any(w in q_lower for w in ["car", "vehicle", "truck", "bike", "plate"]):
            filters["target_type"] = "vehicle"
        elif any(w in q_lower for w in ["person", "suspect", "individual", "man", "woman", "guy"]):
            filters["target_type"] = "person"

        # Colors
        color_list = ["black", "dark", "white", "blue", "red", "green", "gray", "grey", "yellow", "brown"]
        for c in color_list:
            if c in q_lower:
                filters["colors"].append(c)

        # Camera detection: "camera 1", "camera 02", "cam 3", "entrance", "parking", "vault"
        cam_match = re.search(r'camera\s*0?(\d+)|cam\s*0?(\d+)', q_lower)
        if cam_match:
            cam_num = cam_match.group(1) or cam_match.group(2)
            filters["camera"] = f"Camera {int(cam_num):02d}"
        elif "entrance" in q_lower:
            filters["camera"] = "Entrance"
        elif "parking" in q_lower:
            filters["camera"] = "Parking Area"
        elif "vault" in q_lower or "corridor" in q_lower:
            filters["camera"] = "Corridor"

        # Time constraints: "after 7 PM", "before 8:30 PM"
        time_after_match = re.search(r'after\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)', q_lower)
        if time_after_match:
            filters["time_after"] = time_after_match.group(1).upper()

        time_before_match = re.search(r'before\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)', q_lower)
        if time_before_match:
            filters["time_before"] = time_before_match.group(1).upper()

        # Masked search
        if "mask" in q_lower or "covered" in q_lower or "hoodie" in q_lower:
            filters["is_masked"] = True

        # Gait speed
        if any(w in q_lower for w in ["fast", "running", "hurry", "quick", "brisk"]):
            filters["gait_speed"] = "fast"
        elif any(w in q_lower for w in ["slow", "lingering", "stayed", "standing"]):
            filters["gait_speed"] = "slow"

        return filters
