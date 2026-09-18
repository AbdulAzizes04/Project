# GuidedGuard Methodology: Scam-Guided Behavioral Risk Assessment

## 1. Problem Formulation: APP Scam vs. Unauthorized Fraud

Digital payment fraud has fundamentally transformed over the past decade:

| Attribute | Unauthorized Fraud (Credential Theft / ATO) | Scam-Guided Fraud (Authorised Push Payment / APP) |
|---|---|---|
| **Payer Authentication** | Fraudster steals credentials, session tokens, or card | **Legitimate account holder** willingly authenticates |
| **Authentication Flow** | Failed 2FA, brute-force OTP, unknown credential usage | **Valid 2FA/Biometric** supplied by victim under deception |
| **User State** | Unaware until notification received | Actively engaged, often stressed/coached in real-time |
| **Transaction Pattern** | Rapid balance drain to multiple accounts | Single high-value transfer or escalating trial sequence |
| **Scam Archetypes** | Malware, SIM swap, phishing credential harvesters | Impersonation (police, tax, bank), investment, romance |
| **Detection Window** | Account takeover anomalies (login location, browser) | **Authorization-time behavioral & payee deviation** |

In Authorised Push Payment (APP) scams, standard authentication mechanisms (SMS OTP, biometric recognition, hardware tokens) provide zero defense because the victim performs the authentication themselves. Detection must therefore shift from *credential identity validation* to *transactional and behavioral intent analysis*.

---

## 2. Research & Modeling Methodology

GuidedGuard formulates APP scam detection as a **calibrated, multi-modal risk scoring problem** operating strictly prior to fund release:

$$\mathcal{R}(\mathbf{x}) = f_{\text{fusion}}\big(P_{\text{ML}}(\mathbf{x}), A_{\text{IF}}(\mathbf{x}), D_{\text{behav}}(\mathbf{x}), \mathbf{S}_{\text{domain}}(\mathbf{x})\big) \in [0, 100]$$

### Methodology Pipeline:
1. **Target Isolation**: Clean ground-truth fraud indicator without circular post-settlement features.
2. **Temporal Splitting**: Partition data chronologically ($T_{\text{train}} < T_{\text{val}} < T_{\text{test}}$) to preserve the arrow of time.
3. **Dual-Model Training**:
   - Supervised gradient-boosted trees (XGBoost) trained with balanced class weights on historical authorization features.
   - Unsupervised Isolation Forest fitted strictly on legitimate transactions ($\mathcal{D}_{\text{legit}}$) to establish the normative manifold.
4. **Probability Calibration**: Platt scaling (Sigmoid) on the validation partition to map raw margins to empirical posterior probabilities:
   $$\hat{P}(Y=1|\mathbf{x}) = \frac{1}{1 + \exp(A \cdot f(\mathbf{x}) + B)}$$
5. **Multi-Signal Risk Fusion**: Linear weighting across 8 orthogonal risk indicators, producing a 0–100 composite risk index.
6. **Interpretability & Recourse**: Per-transaction SHAP local attributions, LIME surrogate rules, and minimal counterfactual perturbations.

---

## 3. Behavioral Baseline Profiling

To identify social engineering, GuidedGuard constructs per-customer historical profiles:

- **Amount Central Tendency & Dispersion**: $\mu_i = \text{mean}(A_i)$, $\sigma_i = \text{std}(A_i)$
- **Z-Score Deviation**: $Z = \frac{A_{\text{current}} - \mu_i}{\sigma_i + \epsilon}$
- **Amount-to-Average Ratio**: $R = \frac{A_{\text{current}}}{\mu_i + \epsilon}$
- **Recipient Familiarity**: $I_{\text{new\_payee}} = \mathbf{1}[D_{\text{dest}} \notin \mathcal{B}_i]$
- **Temporal Habituation**: Deviation from habitual active hour windows $\mathcal{H}_i$
- **Device & Location Novelty**: Access from non-whitelisted device fingerprints or geographic regions.

---

## 4. Addressing Extreme Class Imbalance

With fraudulent transactions comprising approximately 1.12% of the dataset, traditional Accuracy is degenerate ($98.88\%$ baseline by predicting all legitimate). GuidedGuard evaluates models using imbalance-tailored metrics:
- **Primary Objective**: Precision-Recall AUC (PR-AUC)
- **Calibration Health**: Brier Score Loss ($\frac{1}{N}\sum (p_i - y_i)^2$)
- **Operational Triage**: Precision@K and Recall@K (evaluating fixed analyst workload capacity, e.g., $K=50, 100$).
