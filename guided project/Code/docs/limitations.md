# GuidedGuard Academic Limitations & Future Research Roadmap

## 1. Academic Honesty & Prototype Scope

GuidedGuard is an advanced **final-year B.Tech academic research prototype** developed to investigate explainable behavioral risk assessment for scam-guided (Authorised Push Payment) digital payment fraud. 

To maintain the highest standards of scientific and engineering integrity, this document explicitly details the constraints, assumptions, and boundaries of the current implementation.

---

## 2. Key Limitations

### 2.1 Synthetic Dataset Constraints (PaySim)
- PaySim is generated via an agent-based multi-agent simulator (`PaySimSimulator`) calibrated on aggregate mobile money logs from a developing financial ecosystem.
- While it captures aggregate macro-statistical distributions, synthetic agents do not exhibit the full psychological nuance, emotional distress, or conversational coercion present in human APP fraud victims.
- Behavioral baselines (e.g., customer habituation) are approximated across available historical transaction windows rather than multi-year retail banking ledgers.

### 2.2 Feature Proxies vs. Production Banking Telemetry
In real-world retail banking, payment risk engines consume rich hardware and telecommunication telemetry that public research datasets do not contain:
- **Device Identifiers**: In GuidedGuard, client device risk is evaluated via user-agent proxies and synthetic indicators labeled `[SIMULATED FOR PROTOTYPE]`. Production banks employ SDKs (e.g., ThreatMetrix, BioCatch) measuring biometric swipe cadence, gyroscope tremor, and battery status.
- **Geographic Location**: Location anomaly features rely on regional identifiers and IP proxies rather than GPS coordinates.
- **Call-in-Progress Telephony Signals**: Modern telco-bank data sharing (e.g., GSMA Open Gateway) detects whether a customer is actively on an incoming phone call while transferring money—a paramount APP fraud indicator currently beyond standalone transaction datasets.

### 2.3 Legal & Regulatory Scope of Simulated Interventions
- All intervention mechanisms in GuidedGuard (cooling-off holds, SOC escalation, recipient verification prompts) are **STRICTLY SIMULATED** within the Streamlit dashboard environment.
- The software connects to **zero real payment rails** (no live UPI, ACH, SWIFT, or Faster Payments interfaces).
- GuidedGuard does not issue binding financial decisions or alter live account balances.

### 2.4 Epistemological Limits of AI in Scam Detection
- Machine learning models observe statistical correlations in transactional data.
- An AI algorithm **cannot determine or prove** the psychological state, intent, or mental coercion of a human being.
- Outputs are calibrated risk indices representing *characteristics consistent with scam patterns*, never definitive proof of deception.

---

## 3. Future Research Directions

1. **Telephony & Call-in-Progress Integration**: Integrating real-time telco API webhooks to cross-reference payment execution against active phone call duration.
2. **Graph Neural Networks (GNNs)**: Constructing dynamic, heterogeneous transaction graphs (Payer $\to$ Payee $\to$ Mule Ring) to identify coordinated money mule distribution networks before liquidation.
3. **Federated Multi-Bank Consortium Learning**: Training behavioral anomaly models across multiple institutions without sharing raw customer PII, addressing privacy-preserving cross-bank mule tracking.
4. **Behavioral Biometrics**: Incorporating touchscreen swipe dynamics, hesitation intervals, and copy-paste detection on payee account numbers.
