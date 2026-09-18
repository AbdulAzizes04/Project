"""
QuantumMedCompress Configuration Module.
Centralizes all hyperparameters, reproducibility seeds, file paths, and model settings.
"""

from pathlib import Path
import os
import sys
import torch

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
BACKEND_DIR = BASE_DIR / "backend"
DATASETS_DIR = BASE_DIR / "datasets"
SAVED_MODELS_DIR = BASE_DIR / "saved_models"
RESULTS_DIR = BASE_DIR / "results"
PLOTS_DIR = RESULTS_DIR / "plots"
TABLES_DIR = RESULTS_DIR / "tables"
EXPERIMENTS_DIR = BASE_DIR / "experiments"

# Ensure runtime directories exist
for directory in [DATASETS_DIR, SAVED_MODELS_DIR, RESULTS_DIR, PLOTS_DIR, TABLES_DIR, EXPERIMENTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Database
DB_PATH = BACKEND_DIR / "quantum_med_compress.db"

# Reproducibility
RANDOM_SEED = 42

# Image Preprocessing Settings
IMAGE_SIZE = (64, 64)  # (H, W)
CHANNELS = 1           # Grayscale medical images
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}

# Model Architecture Settings
LATENT_DIM = 8         # Classical latent bottleneck dimension
NUM_QUBITS = 4         # Parameterized quantum circuit qubits
NUM_QUANTUM_LAYERS = 2 # Variational ansatz rotation/entanglement repetitions
QUANTUM_DEVICE = "default.qubit"  # PennyLane analytic statevector simulator

# Training Hyperparameters
BATCH_SIZE = 16
LEARNING_RATE = 1e-3
WEIGHT_DECAY = 1e-4
EPOCHS = 15
SSIM_LOSS_WEIGHT = 0.15 # Loss = MSE + weight * (1 - SSIM)

# Compute Device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Safety & Legal Notice
MEDICAL_DISCLAIMER = (
    "This system is intended strictly for research and educational purposes only "
    "and must not be used for clinical diagnosis or treatment decisions."
)
