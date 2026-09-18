"""
Hybrid Loss Formulation for Bitemporal Environmental Change Segmentation.
L = λ1 * L_CE + λ2 * L_Dice + λ3 * L_Focal
Default configurable weights:
λ1 (Cross Entropy) = 0.30
λ2 (Dice Loss)     = 0.40
λ3 (Focal Loss)    = 0.30
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any

class DiceLoss(nn.Module):
    """
    Multiclass / Binary Dice Loss for semantic segmentation.
    """
    def __init__(self, smooth: float = 1e-5):
        super().__init__()
        self.smooth = smooth

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        probs = F.softmax(logits, dim=1)
        num_classes = logits.shape[1]

        # One-hot encode targets
        targets_one_hot = F.one_hot(targets, num_classes=num_classes).permute(0, 3, 1, 2).float()

        intersection = torch.sum(probs * targets_one_hot, dim=(2, 3))
        cardinality = torch.sum(probs + targets_one_hot, dim=(2, 3))

        dice = (2.0 * intersection + self.smooth) / (cardinality + self.smooth)
        return 1.0 - torch.mean(dice)

class FocalLoss(nn.Module):
    """
    Focal Loss targeting class imbalance between changed and unchanged pixels.
    FL(p_t) = -α_t * (1 - p_t)^γ * log(p_t)
    """
    def __init__(self, alpha: float = 0.25, gamma: float = 2.0):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        ce_loss = F.cross_entropy(logits, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * ((1.0 - pt) ** self.gamma) * ce_loss
        return torch.mean(focal_loss)

class HybridChangeLoss(nn.Module):
    """
    Configurable Hybrid Loss combining Cross Entropy, Dice, and Focal Losses.
    """
    def __init__(
        self,
        weight_ce: float = 0.30,
        weight_dice: float = 0.40,
        weight_focal: float = 0.30,
        focal_alpha: float = 0.25,
        focal_gamma: float = 2.0
    ):
        super().__init__()
        self.weight_ce = weight_ce
        self.weight_dice = weight_dice
        self.weight_focal = weight_focal

        self.ce = nn.CrossEntropyLoss()
        self.dice = DiceLoss()
        self.focal = FocalLoss(alpha=focal_alpha, gamma=focal_gamma)

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> Dict[str, torch.Tensor]:
        l_ce = self.ce(logits, targets)
        l_dice = self.dice(logits, targets)
        l_focal = self.focal(logits, targets)

        total_loss = (
            self.weight_ce * l_ce +
            self.weight_dice * l_dice +
            self.weight_focal * l_focal
        )

        return {
            "total_loss": total_loss,
            "ce_loss": l_ce,
            "dice_loss": l_dice,
            "focal_loss": l_focal
        }
