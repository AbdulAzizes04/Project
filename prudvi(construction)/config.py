"""
BuildVerse AI - Global Configuration File
Defines paths, database configurations, theme tokens, and default parameters.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_IMAGES = UPLOADS_DIR / "images"
UPLOADS_VIDEOS = UPLOADS_DIR / "videos"
UPLOADS_DRONE = UPLOADS_DIR / "drone"
UPLOADS_REPORTS = UPLOADS_DIR / "reports"
UPLOADS_FLOORPLANS = UPLOADS_DIR / "floorplans"
UPLOADS_2D = UPLOADS_DIR / "2d" # 2D Architectural Blueprints directory
ASSETS_DIR = BASE_DIR / "assets"
MODELS_DIR = BASE_DIR / "models"
DATABASE_DIR = BASE_DIR / "database"
DB_PATH = DATABASE_DIR / "buildverse.db"

# Create directories if they don't exist
for folder in [
    UPLOADS_DIR, UPLOADS_IMAGES, UPLOADS_VIDEOS, UPLOADS_DRONE,
    UPLOADS_REPORTS, UPLOADS_FLOORPLANS, UPLOADS_2D, ASSETS_DIR, MODELS_DIR, DATABASE_DIR
]:
    folder.mkdir(parents=True, exist_ok=True)

# Theme Configuration (Strictly White BG, Cyan Primary, Semi-Cyan Secondary, Black Text)
THEME = {
    "bg_color": "#FFFFFF",
    "card_bg": "#F8FAFC",
    "primary_cyan": "#0891B2",      # Rich Vibrant Cyan
    "secondary_cyan": "#06B6D4",    # Lighter Cyan
    "semi_cyan": "#E0F2FE",         # Translucent/Pastel Cyan Accent
    "light_cyan_border": "#BAE6FD", # Soft border
    "text_dark": "#0F172A",         # Crisp dark text for max readability
    "text_muted": "#475569",        # Muted subtext
    "accent_green": "#10B981",      # On-schedule status
    "accent_amber": "#F59E0B",      # Minor delay
    "accent_red": "#EF4444",        # Critical delay
}

# Application Metadata
APP_NAME = "BuildVerse AI"
APP_TAGLINE = "Intelligent AI-Powered Digital Twin & Construction Site Platform"
VERSION = "1.0.0"

# Standard Construction Phases
CONSTRUCTION_PHASES = [
    {"name": "Foundation", "weight": 0.10, "color": "#0891B2"},
    {"name": "Columns", "weight": 0.08, "color": "#0284C7"},
    {"name": "Beams", "weight": 0.08, "color": "#0369A1"},
    {"name": "Slab", "weight": 0.12, "color": "#075985"},
    {"name": "Brick Work", "weight": 0.12, "color": "#0D9488"},
    {"name": "Plastering", "weight": 0.08, "color": "#14B8A6"},
    {"name": "Electrical", "weight": 0.08, "color": "#06B6D4"},
    {"name": "Plumbing", "weight": 0.08, "color": "#38BDF8"},
    {"name": "Flooring", "weight": 0.08, "color": "#7DD3FC"},
    {"name": "Painting", "weight": 0.06, "color": "#22D3EE"},
    {"name": "Interior", "weight": 0.07, "color": "#67E8F9"},
    {"name": "Finishing", "weight": 0.05, "color": "#A5F3FC"}
]
