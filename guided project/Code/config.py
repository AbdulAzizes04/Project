"""
Centralized Configuration for GuidedGuard Explainable AI System.

This module stores all global project constants, directory paths, model hyperparameters,
risk threshold definitions, and UI display settings.
"""

from pathlib import Path

# Project Metadata
PROJECT_NAME = "GuidedGuard"
VERSION = "1.0.0"
APP_TITLE = "GuidedGuard – Scam-Guided Digital Payment Detection"
APP_ICON = "🛡️"
PAGE_LAYOUT = "wide"

# Base Paths
BASE_DIR = Path(__file__).resolve().parent

# Data Paths
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
TRANSACTIONS_CSV = DATA_DIR / "transactions.csv"

# Model Paths
MODELS_DIR = BASE_DIR / "models"
SAVED_MODEL_PATH = MODELS_DIR / "saved_model.pkl"
SCALER_PATH = MODELS_DIR / "scaler.pkl"

# Output Paths
OUTPUTS_DIR = BASE_DIR / "outputs"
REPORTS_DIR = OUTPUTS_DIR / "reports"
LOGS_DIR = OUTPUTS_DIR / "logs"

# Assets Paths
ASSETS_DIR = BASE_DIR / "assets"
STYLE_CSS_PATH = ASSETS_DIR / "style.css"

# Model & Random State Settings
RANDOM_STATE = 42
TEST_SIZE = 0.2

# Feature Definitions
RAW_FEATURE_COLUMNS = [
    "transaction_id",
    "timestamp",
    "amount",
    "old_balance_orig",
    "new_balance_orig",
    "old_balance_dest",
    "new_balance_dest",
    "transaction_type",
    "device_type",
    "location",
    "is_scam",
]

NUMERICAL_FEATURES = [
    "amount",
    "old_balance_orig",
    "new_balance_orig",
    "old_balance_dest",
    "new_balance_dest",
    "transaction_velocity",
    "balance_error_orig",
    "balance_error_dest",
]

CATEGORICAL_FEATURES = [
    "transaction_type",
    "device_type",
]

TARGET_COLUMN = "is_scam"

# Risk Scoring Thresholds
RISK_LEVEL_THRESHOLDS = {
    "LOW": (0.0, 0.35),
    "MEDIUM": (0.35, 0.65),
    "HIGH": (0.65, 0.85),
    "CRITICAL": (0.85, 1.0),
}
