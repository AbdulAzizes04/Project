"""
Constants and Enums for EARTH VISION-X Platform.
"""

from enum import Enum
from typing import Dict, List, Tuple

# Environmental Change Categories
CHANGE_CLASSES: List[str] = [
    "No Change",
    "Deforestation",
    "Urban Expansion",
    "Flood Detection",
    "Water Body Changes",
    "Agricultural Changes",
    "Vegetation Loss",
    "Mining Activity",
    "Wildfire Burn Areas",
    "Land Cover Change",
    "Infrastructure Development"
]

# Color Map (RGB Hex & Normalized RGB) for Visualization
CHANGE_COLOR_MAP: Dict[str, str] = {
    "No Change": "#6B7280",                 # Muted Gray
    "Deforestation": "#EF4444",             # Bright Red
    "Urban Expansion": "#3B82F6",           # Blue
    "Flood Detection": "#06B6D4",           # Cyan
    "Water Body Changes": "#1D4ED8",        # Deep Blue
    "Agricultural Changes": "#F59E0B",      # Amber
    "Vegetation Loss": "#DC2626",           # Dark Red
    "Mining Activity": "#8B5CF6",           # Purple
    "Wildfire Burn Areas": "#B45309",       # Dark Orange/Brown
    "Land Cover Change": "#10B981",         # Emerald Green
    "Infrastructure Development": "#EC4899" # Pink
}

class SupportedModels(str, Enum):
    VIT_BASE = "ViT-Base Siamese"
    SWIN_TRANSFORMER = "Swin Transformer Siamese"
    SWIN_CD = "Swin Transformer Siamese"
    SEGFORMER = "SegFormer MiT-B2"

class SupportedLosses(str, Enum):
    CROSS_ENTROPY = "Cross Entropy"
    DICE_LOSS = "Dice Loss"
    FOCAL_LOSS = "Focal Loss"
    HYBRID_LOSS = "Hybrid (CE + Dice + Focal)"

class SupportedOptimizers(str, Enum):
    ADAMW = "AdamW"
    SGD = "SGD"
    LION = "Lion"

class SupportedDatasets(str, Enum):
    SENTINEL2 = "Sentinel-2 L2A"
    LEVIR_CD = "LEVIR-CD"
    SYSU_CD = "SYSU-CD"
    WHU_CD = "WHU-CD"
    LANDSAT = "Landsat 8/9"
    DYNAMIC_EARTHNET = "DynamicEarthNet"

# Default Sentinel-2 Bands
SENTINEL2_BANDS: List[str] = ["B02 (Blue)", "B03 (Green)", "B04 (Red)", "B08 (NIR)", "B11 (SWIR1)", "B12 (SWIR2)"]
