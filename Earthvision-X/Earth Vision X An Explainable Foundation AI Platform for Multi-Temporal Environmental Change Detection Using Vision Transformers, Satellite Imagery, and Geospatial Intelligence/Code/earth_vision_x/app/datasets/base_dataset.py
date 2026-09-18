"""
Base Dataset Abstraction for Bitemporal Change Detection.
"""

import torch
from torch.utils.data import Dataset
from typing import List, Tuple, Dict, Any, Optional
import numpy as np

class BaseChangeDetectionDataset(Dataset):
    def __init__(self, t1_paths: List[str], t2_paths: List[str], mask_paths: Optional[List[str]] = None, transform=None):
        self.t1_paths = t1_paths
        self.t2_paths = t2_paths
        self.mask_paths = mask_paths
        self.transform = transform

    def __len__(self) -> int:
        return len(self.t1_paths)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        raise NotImplementedError("Subclasses must implement __getitem__")
