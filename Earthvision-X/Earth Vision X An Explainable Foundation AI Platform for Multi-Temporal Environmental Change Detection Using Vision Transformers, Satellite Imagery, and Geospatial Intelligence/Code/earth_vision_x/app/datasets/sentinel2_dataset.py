"""
Sentinel-2 and Bitemporal Dataset Loader Implementation.
Handles multi-band and RGB satellite image pairs with associated ground truth change maps.
"""

import numpy as np
import torch
import cv2
from typing import List, Tuple, Optional
from earth_vision_x.app.datasets.base_dataset import BaseChangeDetectionDataset
from earth_vision_x.app.utils.geospatial import GeospatialIO
from earth_vision_x.app.preprocessing.transforms import BitemporalTransforms

class Sentinel2ChangeDataset(BaseChangeDetectionDataset):
    def __init__(
        self,
        t1_paths: List[str],
        t2_paths: List[str],
        mask_paths: Optional[List[str]] = None,
        image_size: int = 256,
        is_training: bool = True
    ):
        super().__init__(t1_paths, t2_paths, mask_paths)
        self.transform_pipeline = BitemporalTransforms(is_training=is_training, image_size=image_size)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        t1_path = self.t1_paths[idx]
        t2_path = self.t2_paths[idx]

        img_t1, _ = GeospatialIO.read_image(t1_path)
        img_t2, _ = GeospatialIO.read_image(t2_path)

        if self.mask_paths and idx < len(self.mask_paths):
            mask_img, _ = GeospatialIO.read_image(self.mask_paths[idx])
            # If 3-channel, take channel 0
            if mask_img.ndim == 3:
                mask_raw = (mask_img[:, :, 0] * 10).astype(np.int64) # map to categorical index
            else:
                mask_raw = mask_img.astype(np.int64)
        else:
            mask_raw = np.zeros((img_t1.shape[0], img_t1.shape[1]), dtype=np.int64)

        t1_tensor, t2_tensor, mask_tensor = self.transform_pipeline(img_t1, img_t2, mask_raw)
        
        if mask_tensor is None:
            mask_tensor = torch.zeros((img_t1.shape[0], img_t1.shape[1]), dtype=torch.long)

        return t1_tensor, t2_tensor, mask_tensor
