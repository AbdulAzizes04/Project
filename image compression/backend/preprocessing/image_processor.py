"""
Medical Image Preprocessing & Dataset Pipeline.
Handles validation, 64x64 grayscale conversion, intensity scaling,
synthetic medical phantom generation, MedMNIST dataset loading, and PyTorch DataLoaders.
"""

from pathlib import Path
import os
import io
import math
from typing import Tuple, Dict, Any, Optional, List, Union
import numpy as np
import cv2
import torch
from torch.utils.data import Dataset, DataLoader
from PIL import Image

from backend.config import (
    IMAGE_SIZE,
    CHANNELS,
    SUPPORTED_EXTENSIONS,
    DATASETS_DIR,
    BATCH_SIZE,
    RANDOM_SEED
)
from backend.utils.helpers import setup_logger, set_seed

logger = setup_logger("ImageProcessor")

class InvalidImageError(ValueError):
    """Raised when an uploaded or input image fails validation checks."""
    pass

def validate_image_file(file_path: Union[Path, str]) -> Dict[str, Any]:
    """
    Validates that a file exists, has a supported medical/standard extension,
    is non-empty, and can be decoded by OpenCV.
    """
    path = Path(file_path)
    if not path.exists():
        raise InvalidImageError(f"Image file does not exist: {path}")
    if path.stat().st_size == 0:
        raise InvalidImageError(f"Image file is empty (0 bytes): {path}")
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise InvalidImageError(
            f"Unsupported file extension '{path.suffix}'. "
            f"Supported extensions: {sorted(list(SUPPORTED_EXTENSIONS))}"
        )
    
    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise InvalidImageError(f"Corrupted image or unable to decode image data: {path}")
    
    return {
        "valid": True,
        "size_bytes": path.stat().st_size,
        "dimensions": (img.shape[1], img.shape[0]), # (width, height)
        "channels": 1 if len(img.shape) == 2 else img.shape[2]
    }

def preprocess_image(
    input_source: Union[Path, str, bytes, np.ndarray, Image.Image],
    target_size: Tuple[int, int] = IMAGE_SIZE
) -> Tuple[torch.Tensor, Dict[str, Any]]:
    """
    Preprocesses any input image into a standardized (1, 1, 64, 64) PyTorch float32 tensor in [0.0, 1.0].
    
    Steps:
    1. Ingestion: Reads file path, byte stream, PIL Image, or NumPy array.
    2. Grayscale Conversion: Converts RGB/RGBA to single-channel 8-bit grayscale.
    3. Resizing: High-quality bicubic / area interpolation to target_size (64x64).
    4. Normalization: Scales uint8 [0, 255] linearly to float32 [0.0, 1.0].
    5. Batch Tensor formatting: Shapes to (1, 1, H, W).
    """
    # 1. Ingestion
    if isinstance(input_source, (str, Path)):
        path = Path(input_source)
        validate_image_file(path)
        img_bgr = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if img_bgr is None:
            raise InvalidImageError(f"Could not read image from {path}")
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        orig_shape = gray.shape
        size_bytes = path.stat().st_size
    elif isinstance(input_source, bytes):
        if len(input_source) == 0:
            raise InvalidImageError("Input byte stream is empty.")
        nparr = np.frombuffer(input_source, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img_bgr is None:
            raise InvalidImageError("Could not decode image bytes.")
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        orig_shape = gray.shape
        size_bytes = len(input_source)
    elif isinstance(input_source, Image.Image):
        gray = np.array(input_source.convert("L"))
        orig_shape = gray.shape
        size_bytes = gray.nbytes
    elif isinstance(input_source, np.ndarray):
        if len(input_source.shape) == 3 and input_source.shape[2] == 3:
            gray = cv2.cvtColor(input_source, cv2.COLOR_RGB2GRAY)
        elif len(input_source.shape) == 3 and input_source.shape[2] == 4:
            gray = cv2.cvtColor(input_source, cv2.COLOR_RGBA2GRAY)
        elif len(input_source.shape) == 2:
            gray = input_source.copy()
        elif len(input_source.shape) == 3 and input_source.shape[0] == 1:
            gray = input_source[0].copy()
        else:
            raise InvalidImageError(f"Unexpected numpy array shape: {input_source.shape}")
        orig_shape = gray.shape
        size_bytes = gray.nbytes
    else:
        raise InvalidImageError(f"Unsupported image input type: {type(input_source)}")

    # Ensure 8-bit uint8 before resizing
    if gray.dtype != np.uint8:
        gray_normalized = (gray - gray.min()) / (gray.max() - gray.min() + 1e-8)
        gray = (gray_normalized * 255.0).astype(np.uint8)

    # 3. Resizing to target_size (64, 64)
    target_h, target_w = target_size
    if gray.shape != (target_h, target_w):
        interpolation = cv2.INTER_AREA if (gray.shape[0] > target_h or gray.shape[1] > target_w) else cv2.INTER_CUBIC
        resized = cv2.resize(gray, (target_w, target_h), interpolation=interpolation)
    else:
        resized = gray.copy()

    # 4. Normalization to [0.0, 1.0]
    float_img = resized.astype(np.float32) / 255.0

    # 5. Tensor creation (1, 1, H, W)
    tensor = torch.from_numpy(float_img).unsqueeze(0).unsqueeze(0)

    metadata = {
        "original_shape": orig_shape,
        "preprocessed_shape": (target_h, target_w),
        "original_size_bytes": size_bytes,
        "min_val": float(float_img.min()),
        "max_val": float(float_img.max()),
        "mean_val": float(float_img.mean())
    }

    return tensor, metadata

def deprocess_image(tensor: torch.Tensor) -> np.ndarray:
    """
    Converts a PyTorch tensor of shape (B, 1, H, W), (1, H, W), or (H, W) in [0.0, 1.0]
    back to a standard uint8 NumPy 2D array in [0, 255].
    """
    if isinstance(tensor, torch.Tensor):
        arr = tensor.detach().cpu().squeeze().numpy()
    else:
        arr = np.array(tensor).squeeze()

    # Clamp to [0, 1] to prevent overflow
    arr = np.clip(arr, 0.0, 1.0)
    uint8_img = (arr * 255.0).round().astype(np.uint8)
    return uint8_img

def generate_difference_heatmap(original: np.ndarray, reconstructed: np.ndarray) -> np.ndarray:
    """
    Computes pixel-wise absolute difference and returns a BGR Jet/Turbo color heatmap.
    """
    if original.shape != reconstructed.shape:
        reconstructed = cv2.resize(reconstructed, (original.shape[1], original.shape[0]))
    
    diff = cv2.absdiff(original, reconstructed)
    # Enhance difference contrast for visual inspection
    diff_norm = cv2.normalize(diff, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
    heatmap = cv2.applyColorMap(diff_norm, cv2.COLORMAP_JET)
    return heatmap

def generate_synthetic_medical_dataset(
    output_dir: Union[Path, str] = DATASETS_DIR / "synthetic_mri",
    num_samples: int = 150
) -> Path:
    """
    Generates realistic synthetic brain MRI / phantom slices (64x64) mathematically.
    Simulates skull perimeter, brain parenchyma, lateral ventricles, cortical sulci,
    and hyper-intense focal features with anatomical variations.
    
    Guarantees complete standalone offline training and test capability.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    set_seed(RANDOM_SEED)

    h, w = IMAGE_SIZE
    y, x = np.ogrid[:h, :w]
    center_y, center_x = h / 2.0, w / 2.0

    logger.info(f"Generating {num_samples} synthetic medical phantom slices in {out_path}...")

    for idx in range(num_samples):
        img = np.zeros((h, w), dtype=np.float32)

        # 1. Cranium / Skull boundary (outer ellipse)
        rx = 26 + np.random.uniform(-1.5, 1.5)
        ry = 29 + np.random.uniform(-1.5, 1.5)
        skull_mask = (((x - center_x) / rx)**2 + ((y - center_y) / ry)**2) <= 1.0
        img[skull_mask] = 0.85 + np.random.uniform(-0.05, 0.05)

        # 2. Brain Parenchyma (inner brain tissue)
        brain_rx, brain_ry = rx - 2.5, ry - 2.5
        brain_mask = (((x - center_x) / brain_rx)**2 + ((y - center_y) / brain_ry)**2) <= 1.0
        img[brain_mask] = 0.45 + np.random.uniform(-0.08, 0.08)

        # 3. Lateral Ventricles (CSF - fluid, low intensity near center)
        v_offset = 5.0 + np.random.uniform(-0.5, 0.5)
        for side in [-1, 1]:
            vx = center_x + side * v_offset
            vy = center_y - 2.0
            ventricle_mask = (((x - vx) / 3.0)**2 + ((y - vy) / 9.0)**2) <= 1.0
            img[ventricle_mask] = 0.12 + np.random.uniform(-0.03, 0.03)

        # 4. Focal contrast variation / anatomical lesion (simulated tissue anomaly)
        if np.random.rand() > 0.4:
            lx = center_x + np.random.uniform(-12, 12)
            ly = center_y + np.random.uniform(-12, 12)
            lr = np.random.uniform(2.5, 5.0)
            lesion_mask = (((x - lx)**2 + (y - ly)**2) <= lr**2) & brain_mask
            img[lesion_mask] = 0.78 + np.random.uniform(-0.05, 0.05)

        # 5. Gaussian noise for realistic imaging sensor artifact
        noise = np.random.normal(0, 0.02, (h, w))
        img = np.clip(img + noise, 0.0, 1.0)

        # Convert to 8-bit image and save
        uint8_img = (img * 255.0).astype(np.uint8)
        filename = out_path / f"mri_slice_{idx:04d}.png"
        cv2.imwrite(str(filename), uint8_img)

    logger.info(f"Successfully generated {num_samples} slices at {out_path}")
    return out_path

class MedicalImageDataset(Dataset):
    """
    PyTorch Dataset for medical images stored in a directory or in-memory arrays.
    """
    def __init__(self, image_paths: List[Path]):
        self.image_paths = image_paths

    def __len__(self) -> int:
        return len(self.image_paths)

    def __getitem__(self, idx: int) -> torch.Tensor:
        path = self.image_paths[idx]
        tensor, _ = preprocess_image(path)
        return tensor.squeeze(0)  # Return shape: (1, 64, 64)

def get_dataloaders(
    data_dir: Path,
    batch_size: int = BATCH_SIZE,
    train_split: float = 0.7,
    val_split: float = 0.15,
    seed: int = RANDOM_SEED
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    Creates reproducible Train, Validation, and Test DataLoaders from an image directory.
    """
    set_seed(seed)
    images = sorted([
        p for p in Path(data_dir).glob("*")
        if p.suffix.lower() in SUPPORTED_EXTENSIONS
    ])
    if len(images) == 0:
        raise FileNotFoundError(f"No valid medical images found in {data_dir}")

    # Shuffle deterministically
    indices = list(range(len(images)))
    random_state = np.random.RandomState(seed)
    random_state.shuffle(indices)

    n_total = len(images)
    n_train = int(n_total * train_split)
    n_val = int(n_total * val_split)

    train_idx = indices[:n_train]
    val_idx = indices[n_train:n_train + n_val]
    test_idx = indices[n_train + n_val:]

    train_paths = [images[i] for i in train_idx]
    val_paths = [images[i] for i in val_idx]
    test_paths = [images[i] for i in test_idx]

    train_loader = DataLoader(MedicalImageDataset(train_paths), batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(MedicalImageDataset(val_paths), batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(MedicalImageDataset(test_paths), batch_size=batch_size, shuffle=False)

    logger.info(
        f"DataLoaders prepared: Train={len(train_paths)}, "
        f"Val={len(val_paths)}, Test={len(test_paths)}"
    )
    return train_loader, val_loader, test_loader
