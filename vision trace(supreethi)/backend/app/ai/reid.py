import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Tuple

class PersonReIdentifier:
    """
    Forensic Re-Identification & Reference Matching Engine.
    Uses lazy loading for ResNet/Deep embedding feature extractor.
    """
    def __init__(self):
        self._model = None
        self._transform = None
        self._device = None
        self._tried_init = False

    def _get_deep_extractor(self):
        if not self._tried_init:
            self._tried_init = True
            try:
                import torch
                import torchvision.models as models
                import torchvision.transforms as transforms
                self._device = "cuda" if torch.cuda.is_available() else "cpu"
                weights = models.ResNet18_Weights.DEFAULT
                model = models.resnet18(weights=weights)
                self._model = torch.nn.Sequential(*list(model.children())[:-1]).to(self._device).eval()
                self._transform = transforms.Compose([
                    transforms.ToPILImage(),
                    transforms.Resize((224, 112)),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                ])
            except Exception as e:
                print(f"[PersonReIdentifier] Deep feature extractor notice (using color-spatial pyramid): {e}")
        return self._model, self._transform, self._device

    def extract_feature_vector(self, image: np.ndarray) -> np.ndarray:
        if image is None or image.size == 0:
            return np.zeros(64, dtype=np.float32)

        model, transform, device = self._get_deep_extractor()
        if model is not None and transform is not None:
            try:
                import torch
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                tensor = transform(rgb).unsqueeze(0).to(device)
                with torch.no_grad():
                    feat = model(tensor).flatten().cpu().numpy()
                norm = np.linalg.norm(feat)
                return (feat / (norm + 1e-6)).astype(np.float32)
            except Exception:
                pass

        # Fast fallback: Color-spatial pyramid histogram
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, w = image.shape[:2]
        upper = hsv[:int(h*0.5), :]
        lower = hsv[int(h*0.5):, :]

        hist_upper = cv2.calcHist([upper], [0, 1], None, [8, 8], [0, 180, 0, 256])
        hist_lower = cv2.calcHist([lower], [0, 1], None, [8, 8], [0, 180, 0, 256])

        cv2.normalize(hist_upper, hist_upper)
        cv2.normalize(hist_lower, hist_lower)
        combined = np.hstack([hist_upper.flatten(), hist_lower.flatten()]).astype(np.float32)
        norm = np.linalg.norm(combined)
        return (combined / (norm + 1e-6)).astype(np.float32)

    def compute_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        if vec1 is None or vec2 is None or len(vec1) == 0 or len(vec2) == 0:
            return 0.0
        if len(vec1) != len(vec2):
            min_len = min(len(vec1), len(vec2))
            vec1 = vec1[:min_len]
            vec2 = vec2[:min_len]
        dot = float(np.dot(vec1, vec2))
        norm1 = float(np.linalg.norm(vec1))
        norm2 = float(np.linalg.norm(vec2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        sim = dot / (norm1 * norm2)
        return max(0.0, min(1.0, (sim + 1.0) / 2.0 if sim < 0 else sim))

    def describe_appearance(self, person_crop: np.ndarray) -> Dict[str, str]:
        if person_crop is None or person_crop.size == 0:
            return {
                "upper": "Dark jacket / outerwear",
                "lower": "Dark trousers",
                "description": "Indistinct dark forensic silhouette"
            }

        h, w = person_crop.shape[:2]
        upper = person_crop[int(h*0.15):int(h*0.55), :]
        lower = person_crop[int(h*0.55):int(h*0.95), :]

        upper_color = self._dominant_color_name(upper)
        lower_color = self._dominant_color_name(lower)

        return {
            "upper": upper_color,
            "lower": lower_color,
            "description": f"Subject wearing {upper_color.lower()} top and {lower_color.lower()} bottoms"
        }

    def _dominant_color_name(self, img_region: np.ndarray) -> str:
        if img_region is None or img_region.size == 0:
            return "Dark clothing"
        hsv = cv2.cvtColor(img_region, cv2.COLOR_BGR2HSV)
        v = np.mean(hsv[:, :, 2])
        s = np.mean(hsv[:, :, 1])
        h = np.mean(hsv[:, :, 0])

        if v < 60:
            return "Black / Dark Charcoal"
        if v > 200 and s < 45:
            return "White / Light Gray"
        if s < 50:
            return "Gray"
        if (h < 15 or h > 165):
            return "Red / Crimson"
        if 15 <= h < 35:
            return "Orange / Brown"
        if 35 <= h < 85:
            return "Green / Olive"
        if 85 <= h < 135:
            return "Blue / Navy Denim"
        if 135 <= h < 165:
            return "Purple / Violet"
        return "Dark Blue / Denim"
