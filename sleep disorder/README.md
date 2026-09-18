# An Explainable AI Framework for Intelligent Multi-Class Sleep Disorder Classification

[![Python 3.11](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Flask 3.0](https://img.shields.io/badge/Framework-Flask-green.svg)](https://flask.palletsprojects.com/)
[![SHAP](https://img.shields.io/badge/XAI-SHAP-orange.svg)](https://shap.readthedocs.io/)
[![Google Gemini](https://img.shields.io/badge/GenAI-Google%20Gemini-purple.svg)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An academic, production-ready final-year B.Tech Artificial Intelligence & Data Science capstone project that performs non-invasive multi-class screening for sleep disorders (**No Sleep Disorder / Healthy Baseline**, **Insomnia**, and **Sleep Apnea**). The framework combines 5 benchmarked machine learning algorithms, transparent Shapley feature attribution (**SHAP**), and **Google Gemini API** for personalized preventive sleep hygiene guidance and clinical PDF assessment reporting.

---

## 1. Abstract
Sleep disorders represent a silent global epidemic directly correlated with hypertension, stroke, heart failure, cognitive dysfunction, and diminished quality of life. Traditional diagnostic pathways rely primarily on overnight in-lab **Polysomnography (PSG)**, which is resource-intensive, expensive, and subject to extended hospital waiting queues. While Machine Learning (ML) classifiers have demonstrated high diagnostic accuracy, their widespread clinical adoption has been severely impeded by their **"black-box"** opacity—clinicians and patients cannot verify the causal rationale behind a prediction.

This project introduces an end-to-end Explainable AI (XAI) clinical decision-support framework. By systematically training and evaluating 5 classification algorithms with Stratified 5-Fold Cross-Validation, identifying the optimal model via balanced **Macro-F1**, decomposing predictions into exact directional contributions using **SHAP (Shapley Additive exPlanations)**, and integrating conversational guidance via the **Google Gemini API**, the system bridges the gap between machine intelligence, clinical trust, and patient-centered preventive medicine.

---

## 2. Problem Statement
1. **Clinical Inaccessibility**: Full PSG studies require specialized hospital sleep laboratories and overnight monitoring, creating massive screening backlogs.
2. **Black-Box Opacity**: Standard deep learning and ensemble ML models do not justify why an individual is flagged for insomnia or apnea, which is clinically unsafe and ethically problematic.
3. **Absence of Actionable Guidance**: Typical ML screening tools output a cold diagnostic label without offering understandable, personalized, non-pharmacological sleep hygiene or lifestyle interventions.

---

## 3. Existing System vs. Proposed System

| Dimension | Existing Systems | Proposed SleepAI Framework |
| :--- | :--- | :--- |
| **Model Interpretability** | Black-box opacity; raw probability outputs without explanation. | **SHAP TreeExplainer** calculating exact feature attributions and risk direction. |
| **Benchmarking** | Arbitrary single algorithm selection without validation. | **5 ML algorithms** systematically benchmarked with 5-Fold Cross-Validation. |
| **Optimization Metric** | Blind accuracy (misleading under class imbalance). | **Macro-F1 Score & ROC-AUC (OVR)** to protect sensitivity for minority classes. |
| **Post-Prediction Guidance** | None or static generic text. | **Context-grounded Google Gemini AI** recommendations and conversational assistant. |
| **Clinical Reporting** | Unformatted on-screen text. | **Publication-grade ReportLab PDF** clinical assessment summary with letterhead. |
| **Role-Based Access** | Single user view. | **Role-Based Access Control (RBAC)**: Patient Dashboard + Admin Analytics Portal. |

---

## 4. Key Features
- **Rigorous Multi-Class Screening**: Differentiates between *Healthy (None)*, *Insomnia*, and *Sleep Apnea*.
- **5-Model Benchmark Suite**: Logistic Regression, Decision Tree, Support Vector Machine (RBF), Random Forest, and XGBoost.
- **Strict No Data Leakage Pipeline**: Imputation, standardization, and One-Hot Encoding fitted strictly on training splits.
- **SHAP Explainable AI**: Feature importance rankings, positive/negative directional risk badges, and stylized horizontal bar charts.
- **Google Gemini Preventive Guidance**: Context-aware sleep hygiene routines, circadian alignment rituals, and red-flag escalation triggers using the new `google-genai` SDK.
- **Offline Fallback Architecture**: Seamlessly falls back to evidence-based clinical routines if the Gemini API key is unavailable or quota is exceeded.
- **Interactive Conversational Assistant**: Grounded chatbot answering patient inquiries based on their latest physiological assessment data.
- **Executive PDF Clinical Report**: Downloadable multi-section PDF summary with patient metadata, risk gauge, SHAP factors, and recommendations.
- **Comprehensive Admin Console**: Population disorder distribution doughnuts, comparative model accuracy bars, and user auditing.
- **100% Passing Test Suite**: 13 automated `pytest` unit/integration tests and 10 end-to-end integration workflows.

---

## 5. System Architecture

```
                                  [ User / Patient Browser ]
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      │                                               │
             [ Public Web Pages ]                             [ REST API Clients ]
                      │                                               │
                      ▼                                               ▼
         ┌─────────────────────────────────────────────────────────────────┐
         │                    Flask Web Application Core                   │
         │  ├── Auth Blueprint (Session Auth & Werkzeug Password Hash)     │
         │  ├── User Blueprint (Dashboard, Assessment History, Profile)    │
         │  ├── Prediction Blueprint (Intake Form, Inference, XAI View)    │
         │  ├── Chatbot Blueprint (Context-Grounded Conversational AI)     │
         │  └── Admin Blueprint (Population Analytics, Model Benchmarks)   │
         └───────────────────────────────┬─────────────────────────────────┘
                                         │
       ┌───────────────────┬─────────────┴───────┬───────────────────┐
       ▼                   ▼                     ▼                   ▼
┌──────────────┐   ┌───────────────┐   ┌───────────────────┐   ┌───────────────┐
│ SQLite + ORM │   │ ML Predictor  │   │  SHAP Explainer   │   │ Gemini GenAI  │
│ - Users      │   │ - Best Model  │   │ - TreeExplainer   │   │ - Guidance    │
│ - Assessment │   │ - Scaler/OHE  │   │ - Matplotlib Bar  │   │ - Fallback    │
│ - SHAP Logs  │   │ - Multi-Class │   │ - Directionality  │   │ - Q&A Chat    │
└──────────────┘   └───────────────┘   └───────────────────┘   └───────────────┘
                                         │
                                         ▼
                        ┌─────────────────────────────────┐
                        │   ReportLab PDF Engine          │
                        │   - Official Screening Report   │
                        └─────────────────────────────────┘
```

---

## 6. Machine Learning Pipeline & Empirical Results

### 6.1 Dataset Demographics
Trained on the canonical **Sleep Health and Lifestyle Dataset**:
- **Sample Size**: 374 clinical observations, 13 raw parameters.
- **Target Distribution**:
  - `None` (Healthy Baseline): 219 records (58.6%)
  - `Sleep Apnea`: 78 records (20.9%)
  - `Insomnia`: 77 records (20.6%)
- **Engineered Features (23 total after transformation)**:
  - Numerical: `Age`, `Sleep Duration`, `Quality of Sleep`, `Physical Activity Level`, `Stress Level`, `Heart Rate`, `Daily Steps`, `Systolic_BP`, `Diastolic_BP`.
  - One-Hot Categorical: `Gender` (2), `Occupation` (11), `BMI Category` (3: Normal, Overweight, Obese).

### 6.2 Empirical Benchmark Results (80/20 Stratified Split)

| Algorithm | Test Accuracy | Precision (Macro) | Recall (Macro) | F1-Score (Macro) | ROC-AUC (OVR) | 5-Fold CV F1 (Mean ± Std) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Random Forest (Champion)** | **93.33%** | **0.9042** | **0.9049** | **0.9009** | **0.9358** | **0.870 (±0.041)** |
| **Support Vector Machine (RBF)** | 90.67% | 0.8770 | 0.8751 | 0.8675 | 0.9575 | 0.877 (±0.027) |
| **Decision Tree** | 90.67% | 0.8654 | 0.8751 | 0.8653 | 0.9085 | 0.856 (±0.037) |
| **XGBoost** | 90.67% | 0.8549 | 0.8633 | 0.8588 | 0.9433 | 0.873 (±0.046) |
| **Logistic Regression** | 89.33% | 0.8683 | 0.8822 | 0.8663 | 0.9490 | 0.889 (±0.016) |

> **Model Selection Rationale**: While all algorithms achieved over 89% accuracy, **Random Forest** achieved the highest **Macro-F1 (0.9009)** and overall accuracy (93.33%), demonstrating superior sensitivity for differentiating between Insomnia and Sleep Apnea under class imbalance.

---

## 7. Mathematical Formulation of SHAP

SHAP values are rooted in classical cooperative game theory, calculating the marginal contribution of feature $i$ across all possible coalitions of features $S$:

$$\phi_i(x) = \sum_{S \subseteq F \setminus \{i\}} \frac{|S|!(|F| - |S| - 1)!}{|F|!} \left[ f_x(S \cup \{i\}) - f_x(S) \right]$$

- **Efficiency**: $\sum_{i \in F} \phi_i(x) = f(x) - E[f(X)]$
- **Symmetry**: If features $i$ and $j$ contribute identically across all subsets, $\phi_i = \phi_j$.
- **Dummy**: If a feature has zero marginal impact, $\phi_i = 0$.
- **Additivity**: Guarantees consistent attribution across tree ensembles.

---

## 8. Technology Stack

- **Backend**: Python 3.11+, Flask 3.0, Flask-SQLAlchemy 3.1, Werkzeug
- **Machine Learning**: Scikit-Learn 1.7, XGBoost 3.2, Pandas, NumPy, Joblib
- **Explainable AI**: SHAP 0.48, Matplotlib (Agg backend)
- **Generative AI**: Official `google-genai` SDK (`gemini-2.5-flash`)
- **Reporting**: ReportLab 5.0 (PDF Engine)
- **Frontend**: HTML5, Vanilla CSS3 (Healthcare Glassmorphism), Bootstrap 5.3, Chart.js 4.4, FontAwesome 6
- **Testing**: Pytest 9.1

---

## 9. Installation & Setup

### Prerequisites
- Python 3.11 or higher installed on Windows, macOS, or Linux.
- Git.

### 1. Clone or Open Project
```bash
cd "d:\projects\sleep disorder"
```

### 2. Set Up Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Open `.env` and configure:
```env
SECRET_KEY=dev_secret_key_sleep_disorder_ai_2026
DATABASE_URL=sqlite:///sleep_health.db

# Optional: Add your Google Gemini Free API Key
# (Obtain free at https://aistudio.google.com/)
GEMINI_API_KEY=your_gemini_api_key_here

PORT=5000
```
> *Note: If no Gemini API key is provided, the application automatically engages its clinical fallback engine with zero interruption to predictions, SHAP, or reporting.*

---

## 10. Training Models from Scratch
To inspect the raw dataset, execute EDA, train all 5 models with 5-fold cross-validation, and serialize artifacts:
```bash
python ml/train.py
```
This generates:
- `models/preprocessor.pkl`
- `models/feature_names.pkl`
- `models/best_model.pkl`
- `models/model_metrics.json`

---

## 11. Running the Web Application
Start the Flask web server:
```bash
python app.py
```
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

### Default Demo Credentials:
- **Patient Account**:
  - Email: `demo@sleepai.org`
  - Password: `demo123`
- **Administrator Account**:
  - Email: `admin@sleepai.org`
  - Password: `admin123`
  - Admin Portal: `http://127.0.0.1:5000/admin/dashboard`

---

## 12. Running Automated Tests
Execute the complete test suite:
```bash
python -m pytest tests/ -v
```
All 13 unit, model, SHAP, Gemini fallback, and API edge-case tests will run.

---

## 13. REST API Documentation

### 1. Submit Screening Prediction
- **Endpoint**: `POST /api/predict`
- **Content-Type**: `application/json`
- **Request Body**:
```json
{
  "Age": 45,
  "Gender": "Male",
  "Occupation": "Engineer",
  "Sleep Duration": 5.5,
  "Quality of Sleep": 4,
  "Physical Activity Level": 30,
  "Stress Level": 8,
  "BMI Category": "Overweight",
  "Systolic_BP": 135,
  "Diastolic_BP": 88,
  "Heart Rate": 80,
  "Daily Steps": 4500
}
```
- **Response (200 OK)**:
```json
{
  "status": "success",
  "assessment_id": 1,
  "predicted_class": "Insomnia",
  "confidence": 60.54,
  "probabilities": {
    "None": 8.4,
    "Insomnia": 60.54,
    "Sleep Apnea": 31.06
  },
  "risk_level": "Moderate Risk (Sleep Initiation / Maintenance)",
  "top_shap_factors": [
    {
      "feature_name": "Diastolic Blood Pressure (mmHg)",
      "shap_value": 0.0678,
      "direction": "Positive",
      "impact_description": "Elevates probability of Insomnia"
    }
  ],
  "recommendations": "### 1. Understanding Your Screening Result...",
  "disclaimer": "This system is intended for educational and preliminary screening purposes only and does not constitute a medical diagnosis."
}
```

### 2. Conversational AI Assistant
- **Endpoint**: `POST /api/chat`
- **Request Body**: `{"message": "Why is my sleep quality poor?"}`
- **Response (200 OK)**: `{"response": "...", "context_used": true}`

### 3. Google Gemini Diagnostic Status
- **Endpoint**: `GET /api/gemini/status`
- **Response (200 OK)**:
```json
{
  "is_connected": true,
  "mode": "Live Google GenAI (Free Tier)",
  "active_model": "gemini-2.5-flash",
  "sdk_version": "google-genai (Official Current SDK)",
  "key_status": "AIza...4X9Q",
  "models_supported": ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
}
```

### 4. Model Benchmark Performance
- **Endpoint**: `GET /admin/api/model-performance`
- **Response (200 OK)**: Full JSON metrics across all 5 benchmarked classifiers.

---

## 14. Academic Viva Voce Guide (Module Explanations)

### Q1: Why did you choose Multi-Class Classification over Binary Classification?
**Answer**: Sleep pathologies present differently: Insomnia involves sleep architecture and psychological arousal, whereas Obstructive Sleep Apnea involves physiological and airway collapse. A binary "disorder vs. no disorder" model lacks actionable clinical differentiation.

### Q2: Why is Macro-F1 preferred over Accuracy for model selection?
**Answer**: In medical datasets, classes are frequently imbalanced. In our dataset, Healthy controls represent 58.6% of patients, while Insomnia (20.6%) and Apnea (20.9%) are minority classes. Accuracy gives disproportionate credit to the majority class, whereas Macro-F1 assigns equal weight to each category, preventing the model from ignoring minority disorders.

### Q3: How does SHAP ensure mathematical consistency compared to standard Feature Importances?
**Answer**: Standard Gini impurity feature importance in Random Forests suffers from consistency decay and favors high-cardinality features. SHAP values satisfy four game-theoretic axioms (Efficiency, Symmetry, Dummy, and Additivity), guaranteeing that if a model is modified so that a feature has higher marginal contribution, its attribution will never decrease.

### Q4: How is data leakage prevented in your preprocessing pipeline?
**Answer**: Preprocessing objects (`StandardScaler` and `OneHotEncoder`) are fitted **strictly on the training partition** ($X_{train}$) after performing a stratified 80/20 train-test split. The validation set, test set, and subsequent live patient inputs are only transformed using the fitted instances without re-fitting.

### Q5: How do you guarantee patient safety with the Generative AI integration?
**Answer**: The Google Gemini integration is sandboxed with explicit system instructions prohibiting diagnostic claims, drug prescriptions, or medication dosage recommendations. Furthermore, the application is fully decoupled: if the Gemini service encounters network latency or API unavailability, the core ML inference and SHAP explainability pipeline operates completely uninterrupted.

---

## 15. Ethical & Medical Disclaimer
> **IMPORTANT NOTICE**: This system is designed and intended solely for **educational, academic research, and preliminary screening decision-support purposes**. It does not constitute a formal clinical diagnosis, medical evaluation, or treatment prescription. Individuals experiencing persistent sleep difficulties, daytime drowsiness, or witnessed breathing pauses should seek evaluation from a board-certified sleep physician or licensed medical doctor.
