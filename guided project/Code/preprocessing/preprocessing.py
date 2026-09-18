"""
Data Preprocessing Module for GuidedGuard.

This module implements a robust, reusable, and modular data preprocessing pipeline
for digital payment fraud detection datasets (PaySim and Bank Account Fraud).

Responsibility:
- Dataset validation (dtypes, infinite values, empty strings, duplicates, schema).
- Automated missing value imputation (numeric median, categorical mode).
- Duplicate record detection and removal.
- Data type conversion and memory optimization.
- Categorical encoding (Label Encoding and One-Hot Encoding).
- Numerical feature scaling (StandardScaler and MinMaxScaler support).
- Non-destructive IQR outlier capping (Winsorization).
- Identifier and constant feature removal.
- Processed dataset I/O handlers.
"""

from typing import Tuple, Dict, Any, List, Optional, Union
from pathlib import Path
import sys
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder, OneHotEncoder

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import config
from utils.helpers import setup_logger

logger = setup_logger(__name__)


def validate_dataset(df: pd.DataFrame, expected_target: Optional[str] = None) -> Dict[str, Any]:
    """Validate dataset integrity."""
    if df.empty:
        raise ValueError("Cannot validate an empty DataFrame.")

    num_rows, num_cols = df.shape
    num_duplicates = int(df.duplicated().sum())
    empty_strings = int((df.select_dtypes(include=['object']) == "").sum().sum())
    
    num_df = df.select_dtypes(include=[np.number])
    inf_count = int(np.isinf(num_df).sum().sum()) if not num_df.empty else 0

    report = {
        "num_rows": num_rows,
        "num_cols": num_cols,
        "duplicate_count": num_duplicates,
        "duplicate_percentage": round((num_duplicates / num_rows) * 100, 3) if num_rows > 0 else 0.0,
        "total_null_count": int(df.isnull().sum().sum()),
        "empty_string_count": empty_strings,
        "infinite_value_count": inf_count,
        "target_present": (expected_target in df.columns) if expected_target else False,
        "column_types": df.dtypes.to_dict(),
    }
    logger.info(f"Dataset Validation Complete: {num_rows} rows, {num_cols} cols, {num_duplicates} dups, {inf_count} infs")
    return report


def handle_missing_values(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Impute missing values automatically."""
    cleaned = df.copy()
    imputation_log = {}

    num_cols = cleaned.select_dtypes(include=[np.number]).columns
    for col in num_cols:
        null_cnt = cleaned[col].isnull().sum()
        if null_cnt > 0:
            median_val = cleaned[col].median()
            cleaned[col] = cleaned[col].fillna(median_val)
            imputation_log[col] = f"Imputed {null_cnt} missing values with Median ({median_val})"

    cat_cols = cleaned.select_dtypes(include=['object', 'category']).columns
    for col in cat_cols:
        null_cnt = cleaned[col].isnull().sum()
        if null_cnt > 0:
            mode_val = cleaned[col].mode()[0]
            cleaned[col] = cleaned[col].fillna(mode_val)
            imputation_log[col] = f"Imputed {null_cnt} missing values with Mode ('{mode_val}')"

    logger.info(f"Missing value imputation complete. Features updated: {len(imputation_log)}")
    return cleaned, imputation_log


def remove_duplicates(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Detect and remove duplicate rows."""
    initial_rows = len(df)
    dedup_df = df.drop_duplicates().copy()
    final_rows = len(dedup_df)
    removed_rows = initial_rows - final_rows

    stats = {
        "initial_rows": initial_rows,
        "final_rows": final_rows,
        "removed_duplicates": removed_rows,
        "dedup_percentage": round((removed_rows / initial_rows) * 100, 3) if initial_rows > 0 else 0.0,
    }
    logger.info(f"Duplicate Handling: Removed {removed_rows} duplicate rows ({stats['dedup_percentage']}%)")
    return dedup_df, stats


def convert_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Convert columns into optimal, clean data types."""
    converted = df.copy()
    for col in converted.columns:
        if converted[col].dtype == "object":
            converted[col] = converted[col].replace(r"^\s*$", np.nan, regex=True)

        if converted[col].dtype == "bool":
            converted[col] = converted[col].astype(int)

    logger.info("Data type conversion and optimization completed.")
    return converted


def encode_features(
    df: pd.DataFrame,
    cat_cols: Optional[List[str]] = None,
    encoding_type: str = "onehot",
    is_training: bool = True,
    encoder_dict: Optional[Dict[str, Any]] = None,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Encode categorical variables."""
    encoded = df.copy()
    if encoder_dict is None:
        encoder_dict = {}

    if cat_cols is None:
        cat_cols = list(encoded.select_dtypes(include=["object", "category"]).columns)

    if not cat_cols:
        return encoded, encoder_dict

    if encoding_type == "label":
        for col in cat_cols:
            if is_training:
                le = LabelEncoder()
                encoded[col] = le.fit_transform(encoded[col].astype(str))
                encoder_dict[col] = le
            else:
                if col in encoder_dict:
                    le = encoder_dict[col]
                    encoded[col] = le.transform(encoded[col].astype(str))
    else:
        encoded = pd.get_dummies(encoded, columns=cat_cols, drop_first=True, dtype=int)

    logger.info(f"Categorical encoding completed using {encoding_type}. Shape: {encoded.shape}")
    return encoded, encoder_dict


def scale_features(
    df: pd.DataFrame,
    num_cols: Optional[List[str]] = None,
    scaler_type: str = "standard",
    scaler: Optional[Any] = None,
    is_training: bool = True,
) -> Tuple[pd.DataFrame, Any]:
    """Scale numerical features using StandardScaler or MinMaxScaler."""
    scaled = df.copy()
    if num_cols is None:
        num_cols = list(scaled.select_dtypes(include=[np.number]).columns)

    if not num_cols:
        return scaled, scaler

    if is_training:
        if scaler_type.lower() == "minmax":
            scaler = MinMaxScaler()
        else:
            scaler = StandardScaler()
        scaled[num_cols] = scaler.fit_transform(scaled[num_cols])
    else:
        if scaler is None:
            from models.model_loader import load_scaler
            scaler = load_scaler()

        if scaler is not None and hasattr(scaler, "transform"):
            try:
                scaled[num_cols] = scaler.transform(scaled[num_cols])
            except Exception as e:
                logger.warning(f"Scaler transform fallback applied ({e}).")
        else:
            logger.warning("Fitted scaler artifact not present during inference. Preserving raw features.")

    logger.info(f"Numerical feature scaling completed using {scaler_type}. Scaled columns: {len(num_cols)}")
    return scaled, scaler


def handle_outliers(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    method: str = "iqr",
    factor: float = 1.5,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Cap extreme numerical outliers using Interquartile Range (IQR) bounds."""
    capped_df = df.copy()
    capping_log = {}

    if columns is None:
        columns = list(capped_df.select_dtypes(include=[np.number]).columns)

    for col in columns:
        q1 = capped_df[col].quantile(0.25)
        q3 = capped_df[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - factor * iqr
        upper_bound = q3 + factor * iqr

        outliers_count = int(((capped_df[col] < lower_bound) | (capped_df[col] > upper_bound)).sum())
        if outliers_count > 0:
            capped_df[col] = np.clip(capped_df[col], lower_bound, upper_bound)
            capping_log[col] = {
                "capped_count": outliers_count,
                "lower_bound": round(lower_bound, 4),
                "upper_bound": round(upper_bound, 4),
            }

    logger.info(f"Outlier capping completed across {len(capping_log)} numerical features.")
    return capped_df, capping_log


def remove_constant_and_id_features(
    df: pd.DataFrame, id_cols: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, List[str]]:
    """Remove constant zero-variance features and non-predictive identifier columns."""
    cleaned = df.copy()
    dropped_cols = []

    if id_cols:
        for col in id_cols:
            if col in cleaned.columns:
                cleaned = cleaned.drop(columns=[col])
                dropped_cols.append(col)

    if len(cleaned) > 1:
        for col in cleaned.columns:
            if cleaned[col].nunique() <= 1:
                cleaned = cleaned.drop(columns=[col])
                dropped_cols.append(col)

    logger.info(f"Dropped {len(dropped_cols)} identifier / zero-variance columns: {dropped_cols}")
    return cleaned, dropped_cols


def save_processed_dataset(df: pd.DataFrame, output_path: Path) -> Path:
    """Save cleaned DataFrame to CSV file inside data/processed/."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Successfully saved processed dataset to: {output_path} ({len(df)} rows, {len(df.columns)} cols)")
    return output_path


def load_processed_dataset(input_path: Path) -> pd.DataFrame:
    """Load clean processed dataset from data/processed/."""
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Processed dataset not found at: {input_path}")
    df = pd.read_csv(input_path)
    logger.info(f"Loaded processed dataset from {input_path} with shape {df.shape}")
    return df


def preprocess_dataset(
    df: pd.DataFrame, scaler: Optional[Any] = None, is_training: bool = False
) -> Tuple[pd.DataFrame, Any]:
    """Preprocess and scale dataset for model training or inference."""
    df_clean, _ = handle_missing_values(df)
    df_clean = convert_dtypes(df_clean)
    num_cols = list(df_clean.select_dtypes(include=[np.number]).columns)
    df_scaled, scaler_obj = scale_features(df_clean, num_cols=num_cols, scaler=scaler, is_training=is_training)
    return df_scaled, scaler_obj


def preprocess_dataset_pipeline(
    df: pd.DataFrame,
    target_col: str,
    id_cols: Optional[List[str]] = None,
    scaler_type: str = "standard",
    encoding_type: str = "onehot",
    apply_outlier_capping: bool = True,
    is_training: bool = True,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Execute end-to-end data preprocessing pipeline."""
    pipeline_report = {}

    pipeline_report["initial_validation"] = validate_dataset(df, expected_target=target_col)
    df_clean, dup_stats = remove_duplicates(df)
    pipeline_report["duplicate_handling"] = dup_stats
    df_clean, imp_log = handle_missing_values(df_clean)
    pipeline_report["imputation_log"] = imp_log
    df_clean = convert_dtypes(df_clean)
    df_clean, dropped_ids = remove_constant_and_id_features(df_clean, id_cols=id_cols)
    pipeline_report["dropped_id_features"] = dropped_ids

    target_series = None
    if target_col in df_clean.columns:
        target_series = df_clean[target_col]
        df_features = df_clean.drop(columns=[target_col])
    else:
        df_features = df_clean

    if apply_outlier_capping:
        num_cols = list(df_features.select_dtypes(include=[np.number]).columns)
        df_features, capping_log = handle_outliers(df_features, columns=num_cols)
        pipeline_report["outlier_capping"] = capping_log

    cat_cols = list(df_features.select_dtypes(include=["object", "category"]).columns)
    df_features, encoders = encode_features(
        df_features, cat_cols=cat_cols, encoding_type=encoding_type, is_training=is_training
    )
    pipeline_report["encoders"] = encoders

    num_cols = list(df_features.select_dtypes(include=[np.number]).columns)
    df_features, scaler = scale_features(
        df_features, num_cols=num_cols, scaler_type=scaler_type, is_training=is_training
    )
    pipeline_report["scaler"] = scaler

    if target_series is not None:
        df_features[target_col] = target_series.values

    pipeline_report["final_shape"] = df_features.shape
    return df_features, pipeline_report


# Convenience aliases and wrappers for testing and lightweight pipelines
def validate_dataset_schema(df: pd.DataFrame, required_cols: Optional[List[str]] = None) -> Tuple[bool, List[str]]:
    """Validate DataFrame contains all required raw schema columns."""
    if required_cols is None:
        required_cols = ["amount", "step", "type", "oldbalanceOrg"]
    missing = [c for c in required_cols if c not in df.columns]
    return len(missing) == 0, missing


def clean_raw_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Convenience cleaner handling nulls and clamping invalid negative amounts."""
    cleaned, _ = handle_missing_values(df)
    if "amount" in cleaned.columns:
        cleaned["amount"] = np.maximum(0.0, cleaned["amount"].fillna(0.0))
    return cleaned


def preprocess_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """Lightweight preprocessing pipeline returning clean DataFrame."""
    return clean_raw_dataset(df)
