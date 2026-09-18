"""
Helper Functions & Utilities for GuidedGuard.

This module provides common application support functions including logging initialization,
Streamlit CSS style injection, and currency / number formatting helpers.

Responsibility:
- Configure standardized Python logger writing to stdout and log files.
- Inject custom CSS files into Streamlit frontend.
- Provide data formatting utilities.
"""

import logging
from typing import Any, Optional, Dict
from pathlib import Path
import numpy as np
import streamlit as st
import config


def setup_logger(name: str = "GuidedGuard") -> logging.Logger:
    """
    Configure and return a Python logger instance.

    Parameters:
        name (str): Name of the logger module.

    Returns:
        logging.Logger: Configured logger object.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # Console handler
        c_handler = logging.StreamHandler()
        c_format = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s")
        c_handler.setFormatter(c_format)
        logger.addHandler(c_handler)

        # File handler if log dir exists
        config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        file_path = config.LOGS_DIR / "system.log"
        f_handler = logging.FileHandler(file_path)
        f_handler.setFormatter(c_format)
        logger.addHandler(f_handler)

    return logger


def load_css(css_file_path: Path = config.STYLE_CSS_PATH) -> None:
    """
    Load custom CSS stylesheet into Streamlit app.

    Parameters:
        css_file_path (Path): Path to CSS file.
    """
    if css_file_path.exists():
        with open(css_file_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


def format_currency(amount: float) -> str:
    """
    Format numerical float into currency string format.

    Parameters:
        amount (float): Raw currency value.

    Returns:
        str: Formatted currency string ($X,XXX.XX).
    """
    try:
        return f"${float(amount):,.2f}"
    except (ValueError, TypeError):
        return str(amount)


def format_feature_name(col_name: str) -> str:
    """
    Convert technical feature column names into clean human-readable labels.
    """
    name_map = {
        "amount": "Transaction Amount",
        "oldbalanceOrg": "Sender Old Balance",
        "old_balance_orig": "Sender Old Balance",
        "newbalanceOrig": "Sender New Balance",
        "new_balance_orig": "Sender New Balance",
        "oldbalanceDest": "Receiver Old Balance",
        "old_balance_dest": "Receiver Old Balance",
        "newbalanceDest": "Receiver New Balance",
        "new_balance_dest": "Receiver New Balance",
        "step": "Time Step (Hours)",
        "velocity_6h": "6h Transaction Velocity",
        "transaction_velocity": "6h Transaction Velocity",
        "device_type": "Device Type",
        "location": "Location Region",
        "is_new_beneficiary": "New Beneficiary Flag",
        "is_late_night": "Late Night Flag",
        "beneficiary_fraud_history_flag": "Beneficiary Fraud History",
        "balance_wipeout_orig": "Sender Account Wipeout Flag",
        "dest_balance_change": "Receiver Balance Delta",
        "orig_balance_change": "Sender Balance Delta",
        "relative_amount": "Amount vs Balance Ratio",
        "type_CASH_OUT": "Type: Cash Out",
        "type_TRANSFER": "Type: Transfer",
        "type_PAYMENT": "Type: Payment",
        "type_DEBIT": "Type: Debit",
        "type_CASH_IN": "Type: Cash In",
        "high_risk_region_flag": "High Risk Region Flag",
        "recent_transaction_spike": "Txn Spike Flag",
    }
    if col_name in name_map:
        return name_map[col_name]

    # Clean generic column name
    clean = col_name.replace("_", " ").title()
    return clean


def format_feature_value(col_name: str, val: Any, raw_payload: Optional[dict] = None) -> str:
    """
    Format actual feature values nicely with context (e.g. $15,000.00, 6 transactions, Unknown Proxy).
    """
    payload = raw_payload or {}

    col_lower = str(col_name).lower()
    
    # Currency fields
    if any(k in col_lower for k in ["amount", "balance", "delta"]):
        try:
            return format_currency(float(val))
        except (ValueError, TypeError):
            pass

    # Payload overrides for categorical/contextual values
    if "device" in col_lower and "device_type" in payload:
        return str(payload["device_type"])
    if "location" in col_lower or "region" in col_lower:
        if "location" in payload:
            return str(payload["location"])
    if "velocity" in col_lower or "spike" in col_lower:
        if "velocity_6h" in payload:
            return f"{payload['velocity_6h']} txns"
        try:
            return f"{int(float(val))} txns"
        except (ValueError, TypeError):
            pass
    if "beneficiary" in col_lower and "is_new_beneficiary" in payload:
        return "Yes (New)" if int(payload["is_new_beneficiary"]) == 1 else "No (Known)"
    if "fraud_history" in col_lower and "beneficiary_fraud_history_flag" in payload:
        return "Yes (High Risk)" if int(payload["beneficiary_fraud_history_flag"]) == 1 else "No"
    if "type" in col_lower and "transaction_type" in payload:
        return str(payload["transaction_type"])

    # Boolean flags
    if isinstance(val, (bool, np.bool_)):
        return "Yes" if val else "No"

    try:
        fval = float(val)
        if fval.is_integer() and abs(fval) < 10000:
            return str(int(fval))
        elif abs(fval) >= 1000:
            return f"{fval:,.2f}"
        else:
            return f"{fval:.4f}".rstrip("0").rstrip(".")
    except (ValueError, TypeError):
        return str(val)

