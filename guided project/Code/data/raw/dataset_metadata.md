# GuidedGuard Raw Dataset Metadata Documentation

This document records the specifications, origin, target variables, statistics, and integrity verification for all primary raw datasets stored in `data/raw/`.

---

## 1. PaySim Mobile Money Fraud Dataset

- **Dataset Name**: PaySim Financial Transaction Dataset
- **Source**: Kaggle / Synthetic Financial Simulator (PaySim)
- **Download Link**: [Kaggle - PaySim Synthetic Financial Datasets For Fraud Detection](https://www.kaggle.com/datasets/ealaxi/paysim1)
- **Number of Rows**: 25,000
- **Number of Columns**: 11
- **File Size**: 1.944 MB
- **Target Variable**: `isFraud` (1 = Scam/Fraud, 0 = Legitimate)
- **Missing Values**: 0
- **License**: CC BY-SA 4.0
- **Dataset Description**: PaySim simulates mobile money payment transactions based on realistic operational logs from an African financial service provider. It simulates peer-to-peer transfers, merchant payments, cash-ins, and cash-outs.

### Feature Attributes & Types

| Feature Name | Data Type | Description |
| :--- | :--- | :--- |
| `step` | Integer | Hour of simulation timestamp (1 step = 1 hour) |
| `type` | String/Categorical | Transaction category (`PAYMENT`, `TRANSFER`, `CASH_OUT`, `DEBIT`, `CASH_IN`) |
| `amount` | Float | Transaction monetary value in local currency |
| `nameOrig` | String | Unique identifier of originating customer account |
| `oldbalanceOrg` | Float | Initial balance of origin account prior to transaction |
| `newbalanceOrig` | Float | Updated balance of origin account following transaction |
| `nameDest` | String | Unique identifier of destination recipient account |
| `oldbalanceDest` | Float | Initial balance of destination recipient account prior to transaction |
| `newbalanceDest` | Float | Updated balance of destination recipient account following transaction |
| **`isFraud`** | Integer (Target) | Flag indicating fraudulent/scam transaction (1) vs legitimate (0) |
| `isFlaggedFraud` | Integer | System rule flag triggering when transfer amount exceeds threshold |

### Target Distribution

- **Fraud Count (`isFraud == 1`)**: 302 transactions
- **Fraud Percentage**: 1.208%
- **Non-Fraud Count (`isFraud == 0`)**: 24,698 transactions
- **Non-Fraud Percentage**: 98.792%

---

## 2. Bank Account Fraud (BAF) Dataset

- **Dataset Name**: Bank Account Fraud (BAF) Benchmark Suite (NeurIPS 2022)
- **Source**: Kaggle / NeurIPS Datasets and Benchmarks Track
- **Download Link**: [Kaggle - Bank Account Fraud Dataset Suite](https://www.kaggle.com/datasets/sgp94c/bank-account-fraud-baf-suite)
- **Number of Rows**: 20,000
- **Number of Columns**: 21
- **File Size**: 1.518 MB
- **Target Variable**: `fraud_bool` (1 = Fraudulent Application, 0 = Legitimate Application)
- **Missing Values**: 0
- **License**: CC BY 4.0
- **Dataset Description**: BAF is a privacy-preserving synthetic dataset created by Feedzai and NeurIPS 2022 to evaluate fraud models under real-world tabular constraints, incorporating applicant risk scores, velocity indicators, and device fraud counts.

### Key Feature Attributes

| Feature Name | Data Type | Description |
| :--- | :--- | :--- |
| `account_age` | Integer | Age of applicant account in days |
| `month` | Integer | Month index of application |
| `payment_type` | Categorical | Payment method code (`AA`, `AB`, `AC`, `AD`, `AE`) |
| `income` | Float | Quantile normalized applicant income level |
| `employment_status` | Categorical | Employment category code |
| `customer_age` | Integer | Age of applicant in years |
| `velocity_6h` | Float | Velocity indicator for application frequency in past 6 hours |
| `credit_risk_score` | Integer | Applicant credit bureau risk score (300 - 850) |
| `email_is_free` | Integer | Indicator if applicant uses free domain email (1) vs paid (0) |
| `device_fraud_count` | Integer | Historical fraud instances linked to applicant device |
| **`fraud_bool`** | Integer (Target) | Target binary label (1 = Fraud, 0 = Legitimate) |

### Target Distribution

- **Fraud Count (`fraud_bool == 1`)**: 2,557 applications
- **Fraud Percentage**: 12.785%
- **Non-Fraud Count (`fraud_bool == 0`)**: 17,443 applications
- **Non-Fraud Percentage**: 87.215%

---

## 3. Side-by-Side Dataset Comparison

| Comparison Metric | PaySim Dataset (`paysim_transactions.csv`) | Bank Account Fraud Dataset (`baf_base_dataset.csv`) |
| :--- | :--- | :--- |
| **Domain Focus** | Mobile Money Digital Payments & Transfers | Bank Account Opening & Credit Applications |
| **Total Row Count** | 25,000 | 20,000 |
| **Total Feature Count** | 11 | 21 |
| **File Size (MB)** | 1.944 MB | 1.518 MB |
| **Target Variable Name** | `isFraud` | `fraud_bool` |
| **Fraud Rate (%)** | 1.208% | 12.785% |
| **Non-Fraud Rate (%)** | 98.792% | 87.215% |
| **Missing Values Count** | 0 | 0 |
| **Primary Domain Features** | Balance errors, origin/destination balances | Application velocity, credit score, device fraud |
