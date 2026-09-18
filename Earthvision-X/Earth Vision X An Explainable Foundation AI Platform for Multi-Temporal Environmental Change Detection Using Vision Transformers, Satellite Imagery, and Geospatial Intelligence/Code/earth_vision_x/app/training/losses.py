"""
Loss Functions for Bitemporal Segmentation & Change Detection.
Includes Cross Entropy, Dice Loss, Focal Loss, and Hybrid Combination Loss.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from earth_vision_x.app.config.constants import SupportedLosses

class DiceLoss(nn.Module):
    def __init__(self, smooth: float = 1e-6):
        super().__init__()
        self.smooth = smooth

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        num_classes = logits.shape[1]
        probs = F.softmax(logits, dim=1)
        targets_one_hot = F.one_hot(targets, num_classes=num_classes).permute(0, 3, 1, 2).float()

        intersection = torch.sum(probs * targets_one_hot, dim=(2, 3))
        cardinality = torch.sum(probs + targets_one_hot, dim=(2, 3))

        dice_score = (2.0 * intersection + self.smooth) / (cardinality + self.smooth)
        return 1.0 - torch.mean(dice_score)

class FocalLoss(nn.Module):
    def __init__(self, alpha: float = 0.25, gamma: float = 2.0):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        ce_loss = F.cross_entropy(logits, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * ((1 - pt) ** self.gamma) * ce_loss
        return focal_loss.mean()

class HybridLoss(nn.Module):
    def __init__(self, ce_weight: float = 0.4, dice_weight: float = 0.3, focal_weight: float = 0.3):
        super().__init__()
        self.ce = nn.CrossEntropyLoss()
        self.dice = DiceLoss()
        self.focal = FocalLoss()
        self.w1, self.w2, self.w3 = ce_weight, dice_weight, focal_weight

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        l_ce = self.ce(logits, targets)
        l_dice = self.dice(logits, targets)
        l_focal = self.focal(logits, targets)
        return self.w1 * l_ce + self.w2 * l_dice + self.w3 * l_focal

class LossFactory:
    @staticmethod
    def get_loss(loss_name: str | SupportedLosses = SupportedLosses.HYBRID_LOSS) -> nn.Module:
        if loss_name == SupportedLosses.CROSS_ENTROPY or "Cross" in str(loss_name):
            return nn.CrossEntropyLoss()
        elif loss_name == SupportedLosses.DICE_LOSS or "Dice" in str(loss_name):
            return DiceLoss()
        elif loss_name == SupportedLosses.FOCAL_LOSS or "Focal" in str(loss_name):
            return FocalLoss()
        else:
            return HybridLoss()
