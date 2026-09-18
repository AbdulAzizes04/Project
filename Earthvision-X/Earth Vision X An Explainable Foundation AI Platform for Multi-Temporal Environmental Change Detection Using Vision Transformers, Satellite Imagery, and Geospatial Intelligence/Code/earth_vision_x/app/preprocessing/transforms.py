"""
Bitemporal Data Augmentation and Transformation Pipeline.
Ensures identical geometric transforms across Image T1, Image T2, and Change Mask.
Supports Albumentations & PyTorch with pure NumPy/OpenCV fallback.
"""

import numpy as np
import cv2
from typing import Tuple, Dict, Any

try:
    import torch
    TORCH_AVAILABLE = True
except (ImportError, OSError):
    TORCH_AVAILABLE = False

try:
    import albumentations as A
    ALBUMENTATIONS_AVAILABLE = True
except (ImportError, OSError):
    ALBUMENTATIONS_AVAILABLE = False

class BitemporalTransforms:
    def __init__(self, is_training: bool = True, image_size: int = 256):
        self.is_training = is_training
        self.image_size = image_size

        if ALBUMENTATIONS_AVAILABLE:
            if is_training:
                self.spatial_transform = A.Compose([
                    A.Resize(image_size, image_size),
                    A.HorizontalFlip(p=0.5),
                    A.VerticalFlip(p=0.5),
                    A.RandomRotate90(p=0.5),
                ], additional_targets={'image_t2': 'image'})
            else:
                self.spatial_transform = A.Compose([
                    A.Resize(image_size, image_size),
                ], additional_targets={'image_t2': 'image'})

            self.normalize = A.Normalize(
                mean=(0.485, 0.456, 0.406),
                std=(0.229, 0.224, 0.225)
            )

    def __call__(self, img_t1: np.ndarray, img_t2: np.ndarray, mask: np.ndarray = None):
        """
        Applies bitemporal transforms.
        Returns: (t1_tensor/array [3, H, W], t2_tensor/array [3, H, W], mask)
        """
        t1_u = (img_t1 * 255).astype(np.uint8) if img_t1.dtype != np.uint8 and img_t1.max() <= 1.0 else img_t1.astype(np.uint8)
        t2_u = (img_t2 * 255).astype(np.uint8) if img_t2.dtype != np.uint8 and img_t2.max() <= 1.0 else img_t2.astype(np.uint8)

        if ALBUMENTATIONS_AVAILABLE:
            if mask is not None:
                mask_u = mask.astype(np.uint8)
                augmented = self.spatial_transform(image=t1_u, image_t2=t2_u, mask=mask_u)
                mask_aug = torch.tensor(augmented['mask'], dtype=torch.long) if TORCH_AVAILABLE else augmented['mask']
            else:
                augmented = self.spatial_transform(image=t1_u, image_t2=t2_u)
                mask_aug = None

            t1_norm = self.normalize(image=augmented['image'])['image']
            t2_norm = self.normalize(image=augmented['image_t2'])['image']

            if TORCH_AVAILABLE:
                t1_tensor = torch.tensor(t1_norm).permute(2, 0, 1).float()
                t2_tensor = torch.tensor(t2_norm).permute(2, 0, 1).float()
            else:
                t1_tensor = np.transpose(t1_norm, (2, 0, 1)).astype(np.float32)
                t2_tensor = np.transpose(t2_norm, (2, 0, 1)).astype(np.float32)
        else:
            t1_resized = cv2.resize(t1_u, (self.image_size, self.image_size))
            t2_resized = cv2.resize(t2_u, (self.image_size, self.image_size))

            if mask is not None:
                mask_resized = cv2.resize(mask.astype(np.uint8), (self.image_size, self.image_size), interpolation=cv2.INTER_NEAREST)
                mask_aug = torch.tensor(mask_resized, dtype=torch.long) if TORCH_AVAILABLE else mask_resized
            else:
                mask_aug = None

            mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
            std = np.array([0.229, 0.224, 0.225], dtype=np.float32)

            t1_norm = (t1_resized.astype(np.float32) / 255.0 - mean) / std
            t2_norm = (t2_resized.astype(np.float32) / 255.0 - mean) / std

            if TORCH_AVAILABLE:
                t1_tensor = torch.tensor(t1_norm).permute(2, 0, 1).float()
                t2_tensor = torch.tensor(t2_norm).permute(2, 0, 1).float()
            else:
                t1_tensor = np.transpose(t1_norm, (2, 0, 1)).astype(np.float32)
                t2_tensor = np.transpose(t2_norm, (2, 0, 1)).astype(np.float32)

        return t1_tensor, t2_tensor, mask_aug
