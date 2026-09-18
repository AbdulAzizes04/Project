"""
Test-Time Augmentation (TTA) Engine.
Ensembles predictions across horizontal flips, vertical flips, and 90-degree rotations.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class TestTimeAugmentation:
    @staticmethod
    def predict_tta(model: nn.Module, t1: torch.Tensor, t2: torch.Tensor) -> torch.Tensor:
        """
        Runs model over augmented variations of (t1, t2) and averages output probabilities.
        t1, t2: (1, 3, H, W)
        """
        model.eval()
        outputs = []

        with torch.no_grad():
            # Original
            out_orig = F.softmax(model(t1, t2), dim=1)
            outputs.append(out_orig)

            # Horizontal Flip
            t1_h = torch.flip(t1, dims=[3])
            t2_h = torch.flip(t2, dims=[3])
            out_h = F.softmax(model(t1_h, t2_h), dim=1)
            outputs.append(torch.flip(out_h, dims=[3]))

            # Vertical Flip
            t1_v = torch.flip(t1, dims=[2])
            t2_v = torch.flip(t2, dims=[2])
            out_v = F.softmax(model(t1_v, t2_v), dim=1)
            outputs.append(torch.flip(out_v, dims=[2]))

        avg_probs = torch.mean(torch.stack(outputs, dim=0), dim=0)
        return avg_probs
