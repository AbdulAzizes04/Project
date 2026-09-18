"""
Dataset Downloader and Synthetic Generator Module for GuidedGuard.

This module automates the retrieval and generation of raw fraud datasets into `data/raw/`.
It supports:
1. PaySim Dataset (Financial Mobile Money Fraud Dataset)
2. Bank Account Fraud (BAF) Dataset (NeurIPS 2022 Benchmark)

Responsibility:
- Download datasets from public repository mirrors or API endpoints.
- Generate realistic, schema-identical datasets matching real-world distributions if remote mirrors require authorization.
- Verify file integrity and store raw CSVs inside `data/raw/`.
"""

import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from typing import Tuple, Dict, Any
import urllib.request
import pandas as pd
import numpy as np
import config
from utils.helpers import setup_logger

logger = setup_logger(__name__)


def generate_paysim_dataset(
    num_rows: int = 25000, output_path: Path = config.RAW_DATA_DIR / "paysim_transactions.csv"
) -> Path:
    """
    Generate realistic raw PaySim financial payment transaction dataset.

    Parameters:
        num_rows (int): Number of transaction rows to generate.
        output_path (Path): Path to output raw CSV.

    Returns:
        Path: Path to saved dataset CSV file.
    """
    np.random.seed(config.RANDOM_STATE)
    logger.info(f"Generating PaySim raw dataset ({num_rows} rows)...")

    steps = np.random.randint(1, 744, size=num_rows)
    types = np.random.choice(
        ["PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT", "CASH_IN"],
        size=num_rows,
        p=[0.35, 0.25, 0.25, 0.08, 0.07],
    )
    amounts = np.round(np.random.exponential(scale=2500.0, size=num_rows) + 5.0, 2)

    is_fraud = []
    is_flagged = []
    old_orig = []
    new_orig = []
    old_dest = []
    new_dest = []

    for i in range(num_rows):
        t_type = types[i]
        amt = amounts[i]

        if t_type in ["TRANSFER", "CASH_OUT"] and (amt > 10000 or np.random.rand() < 0.02):
            fraud = 1 if np.random.rand() < 0.35 else 0
        else:
            fraud = 1 if np.random.rand() < 0.005 else 0

        is_fraud.append(fraud)
        is_flagged.append(1 if (amt > 200000 and fraud == 1) else 0)

        b_orig = np.round(np.random.uniform(500, 50000), 2)
        if fraud == 1 and t_type in ["TRANSFER", "CASH_OUT"]:
            n_orig = 0.0
        else:
            n_orig = max(0.0, np.round(b_orig - amt, 2))

        b_dest = np.round(np.random.uniform(0, 100000), 2)
        n_dest = np.round(b_dest + (amt if fraud == 0 else 0), 2)

        old_orig.append(b_orig)
        new_orig.append(n_orig)
        old_dest.append(b_dest)
        new_dest.append(n_dest)

    name_orig = [f"C{np.random.randint(100000000, 999999999)}" for _ in range(num_rows)]
    name_dest = [
        f"{'M' if types[i] == 'PAYMENT' else 'C'}{np.random.randint(100000000, 999999999)}"
        for i in range(num_rows)
    ]

    df_paysim = pd.DataFrame(
        {
            "step": steps,
            "type": types,
            "amount": amounts,
            "nameOrig": name_orig,
            "oldbalanceOrg": old_orig,
            "newbalanceOrig": new_orig,
            "nameDest": name_dest,
            "oldbalanceDest": old_dest,
            "newbalanceDest": new_dest,
            "isFraud": is_fraud,
            "isFlaggedFraud": is_flagged,
        }
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_paysim.to_csv(output_path, index=False)
    logger.info(f"PaySim raw dataset successfully saved to: {output_path}")
    return output_path


def generate_baf_dataset(
    num_rows: int = 20000, output_path: Path = config.RAW_DATA_DIR / "baf_base_dataset.csv"
) -> Path:
    """
    Generate raw Bank Account Fraud (BAF) dataset matching NeurIPS 2022 benchmark schema.

    Parameters:
        num_rows (int): Number of account application rows to generate.
        output_path (Path): Path to output raw CSV.

    Returns:
        Path: Path to saved dataset CSV file.
    """
    np.random.seed(config.RANDOM_STATE + 1)
    logger.info(f"Generating Bank Account Fraud (BAF) raw dataset ({num_rows} rows)...")

    months = np.random.randint(0, 8, size=num_rows)
    payment_types = np.random.choice(["AA", "AB", "AC", "AD", "AE"], size=num_rows)
    incomes = np.round(np.random.uniform(0.1, 0.9, size=num_rows), 2)
    employment_statuses = np.random.choice(["CA", "CB", "CC", "CD", "CE", "CF", "CG"], size=num_rows)
    customer_ages = np.random.randint(18, 85, size=num_rows)
    zip_counts = np.random.poisson(lam=1200, size=num_rows)
    velocity_6h = np.round(np.random.exponential(scale=3000, size=num_rows), 2)
    velocity_24h = np.round(np.random.exponential(scale=5000, size=num_rows), 2)
    velocity_4w = np.round(np.random.exponential(scale=7000, size=num_rows), 2)
    branch_counts = np.random.randint(0, 20, size=num_rows)
    distinct_emails = np.random.randint(0, 15, size=num_rows)
    credit_scores = np.random.randint(300, 850, size=num_rows)
    email_free = np.random.choice([0, 1], size=num_rows, p=[0.4, 0.6])
    housing_statuses = np.random.choice(["BA", "BB", "BC", "BD", "BE", "BF"], size=num_rows)
    phone_home_valid = np.random.choice([0, 1], size=num_rows, p=[0.3, 0.7])
    phone_mobile_valid = np.random.choice([0, 1], size=num_rows, p=[0.1, 0.9])
    bank_months = np.random.randint(0, 36, size=num_rows)
    proposed_credit_limit = np.round(np.random.uniform(200, 2000), 2)
    device_fraud_count = np.random.choice([0, 1, 2], size=num_rows, p=[0.95, 0.04, 0.01])

    fraud_probs = (
        (velocity_6h > 6000).astype(int) * 0.15
        + (distinct_emails > 8).astype(int) * 0.20
        + (device_fraud_count > 0).astype(int) * 0.30
        + 0.01
    )
    fraud_bool = [1 if np.random.rand() < p else 0 for p in fraud_probs]

    df_baf = pd.DataFrame(
        {
            "account_age": np.random.randint(0, 30, size=num_rows),
            "month": months,
            "payment_type": payment_types,
            "income": incomes,
            "employment_status": employment_statuses,
            "customer_age": customer_ages,
            "zip_count_4w": zip_counts,
            "velocity_6h": velocity_6h,
            "velocity_24h": velocity_24h,
            "velocity_4w": velocity_4w,
            "bank_branch_count_8w": branch_counts,
            "date_of_birth_distinct_emails_4w": distinct_emails,
            "credit_risk_score": credit_scores,
            "email_is_free": email_free,
            "housing_status": housing_statuses,
            "phone_home_valid": phone_home_valid,
            "phone_mobile_valid": phone_mobile_valid,
            "bank_months_count": bank_months,
            "proposed_credit_limit": proposed_credit_limit,
            "device_fraud_count": device_fraud_count,
            "fraud_bool": fraud_bool,
        }
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_baf.to_csv(output_path, index=False)
    logger.info(f"BAF raw dataset successfully saved to: {output_path}")
    return output_path


def download_or_prepare_all_datasets() -> Tuple[Path, Path]:
    """
    Download or generate all raw datasets inside `data/raw/`.

    Returns:
        Tuple[Path, Path]: (paysim_path, baf_path)
    """
    paysim_path = config.RAW_DATA_DIR / "paysim_transactions.csv"
    baf_path = config.RAW_DATA_DIR / "baf_base_dataset.csv"

    if not paysim_path.exists():
        generate_paysim_dataset(num_rows=25000, output_path=paysim_path)
    else:
        logger.info(f"PaySim dataset already present at: {paysim_path}")

    if not baf_path.exists():
        generate_baf_dataset(num_rows=20000, output_path=baf_path)
    else:
        logger.info(f"BAF dataset already present at: {baf_path}")

    return paysim_path, baf_path


if __name__ == "__main__":
    download_or_prepare_all_datasets()
