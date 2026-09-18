"""
Dataset Schema Adapters for GuidedGuard.

Provides unified interfaces for distinct fraud datasets (PaySim vs Bank Account Fraud - BAF).
Maps only comparable domain features:
- transaction/proposed amount or credit limit
- velocity features (velocity_6h, velocity_24h)
- account tenure / age
- payment / transaction type
- target label harmonization

Prevents forcing incompatible columns into disparate models.
"""

from typing import Tuple, Dict, Any, List
import pandas as pd
import numpy as np


class PaySimAdapter:
    """Adapter for PaySim mobile transaction simulator dataset."""

    @staticmethod
    def adapt(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Extract harmonized features from PaySim."""
        df_out = pd.DataFrame()

        # Target column
        target_col = "isFraud" if "isFraud" in df.columns else df.columns[-1]
        y = df[target_col].astype(int)

        # Core authorization-time parameters
        df_out["amount"] = df["amount"].astype(float)
        df_out["log_amount"] = np.log1p(np.maximum(0, df["amount"]))

        if "step" in df.columns:
            df_out["hour"] = df["step"] % 24
            df_out["day_of_week"] = (df["step"] // 24) % 7
        else:
            df_out["hour"] = 12
            df_out["day_of_week"] = 0

        # One-hot encode type
        if "type" in df.columns:
            type_dummies = pd.get_dummies(df["type"], prefix="type", drop_first=False, dtype=int)
            for col in ["type_CASH_OUT", "type_DEBIT", "type_PAYMENT", "type_TRANSFER"]:
                df_out[col] = type_dummies[col] if col in type_dummies.columns else 0

        # Pre-transaction baseline (old balance)
        if "oldbalanceOrg" in df.columns:
            df_out["oldbalanceOrg"] = df["oldbalanceOrg"].astype(float)
            df_out["log_oldbalanceOrg"] = np.log1p(np.maximum(0, df["oldbalanceOrg"]))
            df_out["amount_to_oldbalance_ratio"] = df["amount"] / (df["oldbalanceOrg"] + 1.0)

        # Beneficiary indicator
        if "nameDest" in df.columns:
            df_out["dest_is_merchant"] = df["nameDest"].astype(str).str.startswith("M").astype(int)

        return df_out, y


class BAFAdapter:
    """Adapter for Bank Account Fraud (BAF - NeurIPS 2022) benchmark dataset."""

    @staticmethod
    def adapt(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Extract harmonized features from BAF."""
        df_out = pd.DataFrame()

        target_col = "fraud_bool" if "fraud_bool" in df.columns else df.columns[-1]
        y = df[target_col].astype(int)

        # Harmonized numerical features
        if "proposed_credit_limit" in df.columns:
            df_out["amount"] = df["proposed_credit_limit"].astype(float)
            df_out["log_amount"] = np.log1p(np.maximum(0, df_out["amount"]))
        elif "income" in df.columns:
            df_out["amount"] = df["income"].astype(float) * 1000.0
            df_out["log_amount"] = np.log1p(np.maximum(0, df_out["amount"]))

        if "velocity_6h" in df.columns:
            df_out["velocity_6h"] = df["velocity_6h"].astype(float)
        if "velocity_24h" in df.columns:
            df_out["velocity_24h"] = df["velocity_24h"].astype(float)

        if "credit_risk_score" in df.columns:
            df_out["risk_score"] = df["credit_risk_score"].astype(float)

        if "customer_age" in df.columns:
            df_out["customer_age"] = df["customer_age"].astype(float)

        if "month" in df.columns:
            df_out["month"] = df["month"].astype(int)

        # Payment type encoding if present
        if "payment_type" in df.columns:
            p_dummies = pd.get_dummies(df["payment_type"], prefix="pay_type", drop_first=False, dtype=int)
            for c in p_dummies.columns:
                df_out[c] = p_dummies[c]

        return df_out, y
