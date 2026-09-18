# GuidedGuard Explainable AI (XAI) & Actionable Recourse

## 1. Interpretability in Payment Scam Detection

In banking fraud operations, opaque black-box machine learning models cannot be deployed responsibly. When a customer's high-value transfer is delayed or placed on a cooling-off hold, regulatory compliance (e.g., Fair Lending, GDPR Article 22) and customer service operations demand **clear, transparent, and actionable rationales**.

GuidedGuard implements a multi-tiered explainability framework:
1. **Game-Theoretic Local Attributions**: SHAP (SHapley Additive exPlanations)
2. **Local Surrogate Decision Rules**: LIME (Local Interpretable Model-agnostic Explanations)
3. **Actionable Counterfactual Recourse**: Minimal actionable perturbations
4. **Natural Language Security Narratives**: Calibrated banking prose without legal liability

---

## 2. SHAP (SHapley Additive exPlanations)

GuidedGuard utilizes **TreeExplainer** optimized for ensemble tree architectures (XGBoost):

$$\phi_i(x) = \sum_{S \subseteq F \setminus \{i\}} \frac{|S|!(|F| - |S| - 1)!}{|F|!} \big[f_x(S \cup \{i\}) - f_x(S)\big]$$

Where:
- $F$ is the set of all authorization-time features ($|F| = 19$).
- $\phi_i(x)$ is the marginal Shapley contribution of feature $i$ to the predicted log-odds margin.
- Efficiency property guarantees local accuracy: $\sum_{i=1}^{M} \phi_i(x) + \phi_0 = f(x)$.

### Visual Outputs:
- **Local Waterfall Plot**: Displays the additive progression from the baseline base expected value $\phi_0$ to the final model prediction, highlighting push factors (positive $\phi_i$, increasing scam risk in red) and pull factors (negative $\phi_i$, reducing scam risk in green).
- **Global Feature Importance**: Ranks features across the entire population by mean absolute attribution: $I_i = \frac{1}{N}\sum_{j=1}^{N} |\phi_i(x_j)|$.

---

## 3. LIME (Local Interpretable Model-agnostic Explanations)

While SHAP provides exact game-theoretic feature shares, **LIME** approximates the complex decision boundary locally around instance $\mathbf{x}$ using a transparent interpretable surrogate model $g \in G$ (ridge regression):

$$\xi(x) = \arg\min_{g \in G} \mathcal{L}(f, g, \pi_x) + \Omega(g)$$

Where:
- $\pi_x(z) = \exp(-D(x, z)^2 / \sigma^2)$ defines the exponential proximity kernel.
- $\Omega(g)$ penalizes surrogate model complexity.

### Output:
LIME translates continuous features into actionable threshold rules, such as:
- $\text{amount} > \$25,000$ (Weight: $+0.34$, pushes toward Scam)
- $\text{amount\_to\_old\_balance\_ratio} > 0.85$ (Weight: $+0.28$)
- $\text{is\_merchant\_dest} = 0$ (Weight: $+0.19$)

---

## 4. Actionable Counterfactual Recourse

Providing a risk score without guidance leaves customers stranded. GuidedGuard's `CounterfactualEngine` generates **minimal actionable perturbations** to answer:

> *"What minimal changes to controllable parameters would bring this transaction's risk score from CRITICAL/HIGH down to LOW/MEDIUM?"*

### Actionable Levers:
1. **Amount Tranching**: Reducing single-payment transfer size closer to the customer's 30-day baseline average ($\mu_A$).
2. **Payee Verification**: Re-authenticating recipient as an established payee via micro-deposit or independent contact.
3. **Execution Timing**: Delaying transfer from late-night hours ($02:00$) to standard business hours ($10:00$).
4. **Channel / Device Trust**: Submitting payment from verified domestic mobile device rather than untrusted proxy network.

---

## 5. Calibrated Security Narrative Engine

### Phrasing Policy & Legal Boundaries:
Machine learning models observe statistical correlations; they cannot legally or scientifically "prove" the mental state of a fraud victim or fraudster. 

**Prohibited Phrasing**:
- ❌ *"This transaction is definitely a scam."*
- ❌ *"Victim is being socially engineered by a cybercriminal."*
- ❌ *"Guaranteed 100% scam probability."*

**Mandated Calibrated Phrasing**:
- ✅ *"This transaction exhibits behavioral and transactional characteristics consistent with elevated scam risk."*
- ✅ *"Observed transfer size represents a 5.2x deviation from the customer's historical 30-day baseline."*
- ✅ *"Protective 30-minute cooling-off hold applied to facilitate customer verification."*
