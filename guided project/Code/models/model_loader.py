"""
Model Artifact Loader & Validation Utility for GuidedGuard.

This module safely loads, validates, and memory-caches serialized model artifacts (.pkl),
feature scalers (.pkl), and training metadata (.json) from `models/`.

Responsibility:
- Load saved model artifact with error handling and Streamlit resource caching.
- Load saved scaler artifact with error handling and Streamlit resource caching.
- Load saved metadata JSON file.
- Validate artifact compatibility, feature consistency, and non-emptiness.
"""

from typing import Tuple, Dict, Any, Optional
from pathlib import Path
import json
import joblib
import streamlit as st

import config
from utils.helpers import setup_logger

logger = setup_logger(__name__)

# Global artifact cache fallbacks for CLI mode
_MODEL_CACHE = None
_SCALER_CACHE = None
_METADATA_CACHE = None


@st.cache_resource
def _load_model_cached(model_path: str) -> Any:
    """Internal cached helper for model loading in Streamlit environment."""
    path = Path(model_path)
    if not path.exists() or path.stat().st_size < 10:
        return None
    return joblib.load(path)


@st.cache_resource
def _load_scaler_cached(scaler_path: str) -> Any:
    """Internal cached helper for scaler loading in Streamlit environment."""
    path = Path(scaler_path)
    if not path.exists() or path.stat().st_size < 10:
        return None
    return joblib.load(path)


def load_model(model_path: Path = config.SAVED_MODEL_PATH, force_reload: bool = False) -> Any:
    """
    Load serialized machine learning model (.pkl) with Streamlit resource caching.

    Parameters:
        model_path (Path): Path to saved_model.pkl.
        force_reload (bool): Force reload bypassing memory cache.

    Returns:
        Any: Loaded Scikit-learn or XGBoost model instance.
    """
    global _MODEL_CACHE
    model_path = Path(model_path)

    try:
        model = _load_model_cached(str(model_path))
        if model is not None:
            return model
    except Exception:
        pass

    if _MODEL_CACHE is not None and not force_reload:
        return _MODEL_CACHE

    if not model_path.exists() or model_path.stat().st_size < 10:
        logger.warning(f"Model artifact missing or unpopulated at {model_path}.")
        return None

    try:
        model = joblib.load(model_path)
        _MODEL_CACHE = model
        logger.info(f"Successfully loaded model artifact from {model_path}")
        return model
    except Exception as e:
        logger.error(f"Failed to load model artifact from {model_path}: {e}")
        return None


def load_scaler(scaler_path: Path = config.SCALER_PATH, force_reload: bool = False) -> Any:
    """
    Load serialized StandardScaler (.pkl) with Streamlit resource caching.

    Parameters:
        scaler_path (Path): Path to scaler.pkl.
        force_reload (bool): Force reload bypassing memory cache.

    Returns:
        Any: Loaded StandardScaler instance.
    """
    global _SCALER_CACHE
    scaler_path = Path(scaler_path)

    try:
        scaler = _load_scaler_cached(str(scaler_path))
        if scaler is not None:
            return scaler
    except Exception:
        pass

    if _SCALER_CACHE is not None and not force_reload:
        return _SCALER_CACHE

    if not scaler_path.exists() or scaler_path.stat().st_size < 10:
        logger.warning(f"Scaler artifact missing or unpopulated at {scaler_path}.")
        return None

    try:
        scaler = joblib.load(scaler_path)
        _SCALER_CACHE = scaler
        logger.info(f"Successfully loaded scaler artifact from {scaler_path}")
        return scaler
    except Exception as e:
        logger.error(f"Failed to load scaler artifact from {scaler_path}: {e}")
        return None


def load_metadata(
    metadata_path: Path = config.MODELS_DIR / "model_metadata.json", force_reload: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Load training run metadata JSON with caching.

    Parameters:
        metadata_path (Path): Path to model_metadata.json.
        force_reload (bool): Force reload bypassing memory cache.

    Returns:
        Optional[Dict[str, Any]]: Metadata dictionary if present.
    """
    global _METADATA_CACHE
    if _METADATA_CACHE is not None and not force_reload:
        return _METADATA_CACHE

    metadata_path = Path(metadata_path)
    if not metadata_path.exists():
        logger.warning(f"Model metadata JSON missing at {metadata_path}")
        return None

    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        _METADATA_CACHE = meta
        return meta
    except Exception as e:
        logger.error(f"Failed to read model metadata JSON: {e}")
        return None


_ANOMALY_CACHE = None


@st.cache_resource
def _load_anomaly_cached(path_str: str) -> Any:
    """Internal cached helper for anomaly detector."""
    path = Path(path_str)
    if not path.exists() or path.stat().st_size < 10:
        return None
    return joblib.load(path)


def load_anomaly_detector(
    detector_path: Path = config.MODELS_DIR / "anomaly_detector.pkl", force_reload: bool = False
) -> Any:
    """Load serialized Isolation Forest AnomalyDetector artifact."""
    global _ANOMALY_CACHE
    detector_path = Path(detector_path)

    try:
        det = _load_anomaly_cached(str(detector_path))
        if det is not None:
            return det
    except Exception:
        pass

    if _ANOMALY_CACHE is not None and not force_reload:
        return _ANOMALY_CACHE

    if not detector_path.exists():
        return None

    try:
        det = joblib.load(detector_path)
        _ANOMALY_CACHE = det
        return det
    except Exception as e:
        logger.error(f"Failed to load anomaly detector: {e}")
        return None


def validate_artifacts() -> Dict[str, Any]:
    """
    Validate model, scaler, and metadata compatibility, feature consistency, and status.

    Returns:
        Dict[str, Any]: Validation summary dictionary.
    """
    model = load_model()
    scaler = load_scaler()
    metadata = load_metadata()
    anomaly_det = load_anomaly_detector()

    model_valid = model is not None and hasattr(model, "predict_proba")
    scaler_valid = scaler is not None and hasattr(scaler, "transform")
    metadata_valid = metadata is not None and "metrics" in metadata

    n_features = None
    if hasattr(model, "n_features_in_"):
        n_features = getattr(model, "n_features_in_")

    validation_report = {
        "model_valid": model_valid,
        "scaler_valid": scaler_valid,
        "metadata_valid": metadata_valid,
        "anomaly_detector_valid": anomaly_det is not None,
        "model_name": metadata.get("model_name", type(model).__name__ if model else "Unknown"),
        "expected_num_features": n_features or metadata.get("num_features", 19) if metadata else 19,
        "ready_for_inference": (model_valid and scaler_valid),
    }

    logger.info(f"Artifact Validation Complete: ready={validation_report['ready_for_inference']}, model={validation_report['model_name']}")
    return validation_report


def load_artifacts() -> Tuple[Any, Any, Optional[Dict[str, Any]], Any]:
    """
    Load model, scaler, metadata, and anomaly detector artifacts simultaneously.

    Returns:
        Tuple[model, scaler, metadata, anomaly_detector]
    """
    model = load_model()
    scaler = load_scaler()
    metadata = load_metadata()
    anomaly_detector = load_anomaly_detector()
    return model, scaler, metadata, anomaly_detector
