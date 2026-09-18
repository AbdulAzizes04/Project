"""
Dataset Loader & Integrity Validator Utility for GuidedGuard.

This module provides reusable functions to safely load, validate, and inspect
raw datasets (PaySim, Bank Account Fraud) from `data/raw/` or custom file paths.

Responsibility:
- Load CSV datasets into Pandas DataFrames with robust error handling.
- Perform dataset integrity and schema validation checks.
- Compute non-destructive dataset summary statistics (row/col count, fraud ratio, file size).
"""

from typing import Tuple, Dict, Any, Optional
from pathlib import Path
import os
import pandas as pd
import numpy as np
from utils.helpers import setup_logger

logger = setup_logger(__name__)


def load_dataset(file_path: Path) -> pd.DataFrame:
    """
    Load CSV dataset safely from the filesystem.

    Parameters:
        file_path (Path): Path to CSV dataset file.

    Returns:
        pd.DataFrame: Loaded dataset DataFrame.

    Raises:
        FileNotFoundError: If the specified file_path does not exist.
        ValueError: If the dataset file is empty or corrupted.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        logger.error(f"Dataset file not found at: {file_path}")
        raise FileNotFoundError(f"Dataset file not found at: {file_path}")

    try:
        df = pd.read_csv(file_path)
        if df.empty:
            logger.error(f"Loaded dataset at {file_path} is empty.")
            raise ValueError(f"Loaded dataset at {file_path} is empty.")
        logger.info(f"Successfully loaded dataset '{file_path.name}' with shape {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Failed to read CSV file '{file_path}': {e}")
        raise ValueError(f"Failed to read CSV file '{file_path}': {e}")


def validate_dataset_schema(
    df: pd.DataFrame, expected_target: str, required_cols: Optional[list] = None
) -> Tuple[bool, Dict[str, Any]]:
    """
    Validate dataset integrity, non-emptiness, target column presence, and missing values.

    Parameters:
        df (pd.DataFrame): Loaded DataFrame to validate.
        expected_target (str): Expected target column name (e.g. 'isFraud' or 'fraud_bool').
        required_cols (Optional[list]): List of essential column names to verify.

    Returns:
        Tuple[bool, Dict[str, Any]]: (is_valid, validation_report_dict)
    """
    report = {
        "num_rows": len(df),
        "num_cols": len(df.columns),
        "target_present": expected_target in df.columns,
        "missing_values": int(df.isnull().sum().sum()),
        "has_required_cols": True,
        "errors": [],
    }

    if df.empty:
        report["errors"].append("DataFrame is empty.")
    if not report["target_present"]:
        report["errors"].append(f"Target column '{expected_target}' not found in columns.")

    if required_cols:
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            report["has_required_cols"] = False
            report["errors"].append(f"Missing required columns: {missing}")

    is_valid = len(report["errors"]) == 0
    return is_valid, report


def get_dataset_summary(df: pd.DataFrame, target_col: str, file_path: Path) -> Dict[str, Any]:
    """
    Calculate summary statistics including file size, row/col count, and class balance ratios.

    Parameters:
        df (pd.DataFrame): Dataset DataFrame.
        target_col (str): Target column name.
        file_path (Path): File path to calculate file size in MB.

    Returns:
        Dict[str, Any]: Summary dictionary with counts, percentages, and data types.
    """
    file_path = Path(file_path)
    file_size_mb = round(file_path.stat().st_size / (1024 * 1024), 3) if file_path.exists() else 0.0

    total_rows = len(df)
    total_cols = len(df.columns)

    if target_col in df.columns:
        scam_counts = df[target_col].value_counts()
        fraud_count = int(scam_counts.get(1, 0))
        non_fraud_count = int(scam_counts.get(0, 0))
        fraud_pct = round((fraud_count / total_rows) * 100, 3) if total_rows > 0 else 0.0
        non_fraud_pct = round((non_fraud_count / total_rows) * 100, 3) if total_rows > 0 else 0.0
    else:
        fraud_count = 0
        non_fraud_count = 0
        fraud_pct = 0.0
        non_fraud_pct = 0.0

    summary = {
        "dataset_name": file_path.name,
        "file_size_mb": file_size_mb,
        "total_rows": total_rows,
        "total_cols": total_cols,
        "target_col": target_col,
        "fraud_count": fraud_count,
        "non_fraud_count": non_fraud_count,
        "fraud_percentage": fraud_pct,
        "non_fraud_percentage": non_fraud_pct,
        "missing_value_count": int(df.isnull().sum().sum()),
    }
    return summary
