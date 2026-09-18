# GuidedGuard Feature Engineering: Authorization-Time Representations

## 1. Feature Representation Philosophy

GuidedGuard models transaction risk at the **instant of payment submission**. This necessitates rigorous separation between:
1. **Pre-Transaction Baselines**: Customer historical behavioral statistics aggregated before transaction submission.
2. **Transaction-Time Parameters**: Observable attributes included in the payment submission payload.
3. **Post-Transaction State**: Prohibited attributes reflecting account balances or clearing outcomes post-settlement.

---

## 2. Complete Dictionary of 19 Clean Authorization Features

| # | Feature Name | Category | Type | Description | Mathematical Formulation / Definition |
|---|---|---|---|---|---|
| 1 | `amount` | Transaction | Float | Nominal payment transfer amount | $A$ in standard currency units |
| 2 | `oldbalanceOrg` | Baseline | Float | Origin account balance prior to transaction | $B_{\text{orig}}$ at authorization time |
| 3 | `log_amount` | Transaction | Float | Logarithmic transformation of transfer amount | $\ln(A + 1)$ |
| 4 | `amount_to_old_balance_ratio` | Risk Ratio | Float | Proportion of liquid capital being transferred | $\frac{A}{B_{\text{orig}} + 1.0}$ |
| 5 | `is_high_portion_of_balance` | Indicator | Binary | Flag indicating transfer $>80\%$ of available funds | $\mathbf{1}\left[\frac{A}{B_{\text{orig}} + 1.0} > 0.8\right]$ |
| 6 | `hour_of_day` | Temporal | Integer | Hour in 24-hour cycle when payment was initiated | $\text{step} \pmod{24} \in [0, 23]$ |
| 7 | `day_of_week` | Temporal | Integer | Day of the week | $\left\lfloor\frac{\text{step}}{24}\right\rfloor \pmod 7 \in [0, 6]$ |
| 8 | `is_weekend` | Temporal | Binary | Flag indicating Saturday or Sunday | $\mathbf{1}[\text{day\_of\_week} \in \{5, 6\}]$ |
| 9 | `is_business_hours` | Temporal | Binary | Flag indicating normal banking window (09:00 - 17:00) | $\mathbf{1}[9 \le \text{hour\_of\_day} \le 17]$ |
| 10 | `is_late_night` | Temporal | Binary | Flag indicating off-hours window (23:00 - 05:00) | $\mathbf{1}[\text{hour\_of\_day} \in \{23, 0, 1, 2, 3, 4\}]$ |
| 11 | `amount_deviation` | Behavioral | Float | Z-score of amount relative to population distribution | $\frac{A - \mu_A}{\sigma_A + \epsilon}$ |
| 12 | `relative_amount` | Behavioral | Float | Ratio of amount to population mean | $\frac{A}{\mu_A + \epsilon}$ |
| 13 | `is_large_transaction` | Risk Ratio | Binary | Transfer exceeds population 90th percentile | $\mathbf{1}[A > P_{90}(A)]$ |
| 14 | `velocity_1h` | Velocity | Float | Estimated transaction count in prior 1-hour window | $V_{1h}$ |
| 15 | `velocity_6h` | Velocity | Float | Estimated transaction count in prior 6-hour window | $V_{6h}$ |
| 16 | `velocity_24h` | Velocity | Float | Estimated transaction count in prior 24-hour window | $V_{24h}$ |
| 17 | `recent_transaction_spike` | Velocity | Binary | Short-term velocity significantly outpaces 6h cadence | $\mathbf{1}\left[V_{1h} > 1.5 \cdot \frac{V_{6h}}{6}\right]$ |
| 18 | `is_merchant_dest` | Beneficiary | Binary | Destination account is an established merchant entity | $\mathbf{1}[\text{nameDest starts with 'M'}]$ |
| 19 | `interaction_amount_x_velocity`| Interaction | Float | Cross-feature interaction of transfer size and urgency | $A \times V_{6h}$ |

---

## 3. Strict Exclusion of Post-Transaction Target Leakage

The following columns are permanently excluded from model training and real-time inference:

| Excluded Column | Leakage Mechanism | Observed Impact if Included |
|---|---|---|
| `newbalanceOrig` | Leaks post-settlement balance. In PaySim, fraudulent transfers set `newbalanceOrig == 0.0`. | Artificial 100% accuracy, memorization of zero-balance. |
| `newbalanceDest` | Leaks recipient account balance change post-clearing. | Bypasses authorization-time uncertainty. |
| `balance_wipeout_orig` | Derived as `(oldbalanceOrg > 500) & (newbalanceOrig == 0)`. | Direct proxy for ground truth fraud label. |
| `balance_diff_orig` | `oldbalanceOrg - newbalanceOrig`. | Trivial arithmetic identity with amount. |
| `balance_error_orig` | `|oldbalanceOrg - amount - newbalanceOrig|`. | Explicitly flags ledger discrepancy. |

Removing these columns yields an honest, defensible evaluation: PR-AUC of **0.0923** on out-of-time test data (an **8.2x lift** over the positive prevalence rate of 1.12%).
