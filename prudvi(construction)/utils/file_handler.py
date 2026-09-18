"""
File Handler utility for uploads and disk management.
"""

import os
from pathlib import Path
from config import UPLOADS_IMAGES, UPLOADS_VIDEOS, UPLOADS_DRONE, UPLOADS_REPORTS, UPLOADS_FLOORPLANS

def save_uploaded_file(uploaded_file, category: str = "images") -> str:
    """Saves Streamlit UploadedFile to local uploads directory and returns path."""
    target_dir_map = {
        "images": UPLOADS_IMAGES,
        "videos": UPLOADS_VIDEOS,
        "drone": UPLOADS_DRONE,
        "reports": UPLOADS_REPORTS,
        "floorplans": UPLOADS_FLOORPLANS
    }
    
    target_dir = target_dir_map.get(category, UPLOADS_IMAGES)
    file_path = target_dir / uploaded_file.name
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    return str(file_path)
