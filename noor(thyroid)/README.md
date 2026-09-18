# 🏥 ThyroAI — Patient-Specific Thyroid Risk Assessment Platform

**Patient-Specific Thyroid Risk Assessment Through Hybrid Explainable Machine Learning**

A production-quality healthcare AI web application for predicting thyroid diseases (Hypothyroidism, Hyperthyroidism, Thyroid Nodules) using an ensemble of 5 machine learning models with SHAP/LIME explainability.

---

## ✨ Features

- 🤖 **5-Model Ensemble ML**: Random Forest + XGBoost + LightGBM + SVM + ANN with weighted voting
- 🔍 **Explainable AI**: SHAP feature importance + LIME local explanations + Natural Language explanations
- 📊 **Clinical Dashboard**: Real-time stats, Pie/Bar/Line/Radar charts
- 📋 **Multi-Step Patient Form**: 6-step form with voice input support
- 📄 **Automated PDF Reports**: With QR codes, SHAP values, recommendations
- 🔬 **OCR Report Extraction**: Auto-extract values from blood report PDFs/images
- 💬 **AI Chat Assistant**: Thyroid knowledge Q&A bot
- 📅 **Appointment Management**: Book, complete, cancel appointments
- 👨‍💼 **Admin Panel**: User management, model metrics, dataset upload, CSV export
- 🌙 **Dark Mode**: Full dark/light theme toggle

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- pip

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

Create a copy of `.env.example` as `.env`:
```bash
copy .env.example .env
```

### 2. Train ML Models
```bash
cd ml_models
python generate_dataset.py   # Generate synthetic dataset
python train.py               # Train all 5 models (~2-5 min)
```

### 3. Start Backend
```bash
cd backend
uvicorn main:app --reload
```
Backend runs at: http://localhost:8000
API Docs: http://localhost:8000/docs

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at: http://localhost:5173

---

## 🔐 Default Login

| Username | Password | Role  |
|----------|----------|-------|
| admin    | admin123 | Admin |

*(Created automatically on first run)*

---

## 📁 Project Structure

```
noor(thyroid)/
├── frontend/               # React + Tailwind + Framer Motion
│   ├── src/
│   │   ├── components/    # Layout, Sidebar, Notifications
│   │   ├── pages/         # All page components
│   │   ├── services/      # Axios API client
│   │   └── store/         # Zustand global state
│   └── package.json
│
├── backend/               # FastAPI
│   ├── main.py           # App entry point
│   ├── routers/          # API routers (auth, patients, predictions...)
│   ├── services/         # ML, SHAP, LIME, PDF services
│   ├── database/         # SQLAlchemy models
│   └── requirements.txt
│
├── ml_models/             # ML training & inference
│   ├── generate_dataset.py
│   ├── train.py
│   └── saved_models/     # Trained model files
│
├── datasets/              # CSV training data
├── uploads/               # Medical scan images
├── reports/               # Generated PDF reports
└── assets/                # Static assets
```

---

## 🧠 Machine Learning Models

| Model         | Weight | Notes                          |
|---------------|--------|--------------------------------|
| Random Forest | 30%    | Primary explainer (SHAP)       |
| XGBoost       | 30%    | Gradient boosting              |
| LightGBM      | 20%    | Fast gradient boosting         |
| SVM           | 10%    | Kernel RBF, probability=True   |
| ANN (Keras)   | 10%    | 3-layer dense neural network   |

**Ensemble**: Weighted probability voting across all 5 models

---

## 🔬 Input Features (36 total)

| Category | Features |
|----------|----------|
| Demographics | Age, Gender, Weight, Height, BMI, Pulse Rate |
| Symptoms | 14 symptoms (Fatigue, Weight Gain/Loss, etc.) |
| Hormones | TSH, T3, T4, FT3, FT4 |
| Blood Tests | Hemoglobin, WBC, RBC, Platelets, Vitamin D, Calcium |
| Medical History | Diabetes, Hypertension, Family History, Smoking, Alcohol |

---

## 📊 Predicted Conditions

- **Healthy** — Normal thyroid function
- **Hypothyroidism** — Underactive thyroid (High TSH, Low FT4)
- **Hyperthyroidism** — Overactive thyroid (Low TSH, High FT4)
- **Thyroid Nodules** — Thyroid gland growths

---

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login |
| GET | `/api/patients/` | List patients |
| POST | `/api/patients/` | Create patient |
| POST | `/api/predictions/` | Run AI prediction |
| GET | `/api/predictions/stats` | Prediction statistics |
| POST | `/api/reports/generate/{id}` | Generate PDF report |
| POST | `/api/ocr/extract` | Extract values from PDF |
| GET | `/api/admin/analytics` | Dashboard analytics |
| GET | `/api/admin/model-performance` | Model metrics |

Full API docs: http://localhost:8000/docs

---

## 🔧 OCR Setup (Optional)

For PDF/image report extraction, install Tesseract:

**Windows:**
```bash
choco install tesseract
# or download from: https://github.com/UB-Mannheim/tesseract/wiki
```

**Linux:**
```bash
sudo apt install tesseract-ocr
```

If Tesseract is not installed, OCR will gracefully fall back to manual entry.

---

## 📧 Email Reports (Optional)

Edit `backend/.env`:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASS=your-app-password
```

---

## 🎨 Tech Stack

**Frontend**: React 18, Tailwind CSS, Framer Motion, Recharts, React Router, MUI, React Icons, Zustand

**Backend**: FastAPI, SQLAlchemy, SQLite, JWT Auth

**ML**: Scikit-Learn, XGBoost, LightGBM, TensorFlow/Keras

**XAI**: SHAP, LIME

**Reports**: ReportLab, QRCode

---

## ⚠️ Disclaimer

> ThyroAI is a clinical decision support tool intended to assist healthcare professionals. It is **not a substitute** for professional medical advice, diagnosis, or treatment. Always consult a qualified physician.
