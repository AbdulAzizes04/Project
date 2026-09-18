# AI-Based Intelligent Public Grievance Redressal System for Automated Complaint Classification and Resolution

An end-to-end, production-style, e-Governance platform designed for academic presentation and real-world municipal grievance redressal. It combines conversational AI dialog with machine learning pipelines to automate complaint intake, text categorization, urgency priority scoring, semantic duplicate detection, department routing, and SLA tracking.

---

## 🌟 Key System Capabilities

1. **Conversational Citizen AI Chatbot (`/chat`)**:
   - Guided conversational dialog extracting incident description, location, duration, and severity in plain English.
   - Real-time pre-submission AI analysis preview showing predicted category, priority, and similarity warnings.
   - Auto-generates formal complaint ticket (`GRV-2026-XXXX`).

2. **NLP Text Classification Engine**:
   - Compares **TF-IDF + LinearSVC (Calibrated with sigmoid)** vs **TF-IDF + Logistic Regression** baseline.
   - Sourced from a stratified dataset of 1,200+ domain records across 6 municipal departments.
   - Calibrated output delivers realistic probability confidence scores (e.g. 94% confidence).

3. **Priority & SLA Prediction Engine**:
   - Gradient Boosting classifier combining TF-IDF n-grams with engineered features (urgency terms, hazard keywords, duration parsing, one-hot category priors).
   - Categorizes into `Low`, `Medium`, `High`, `Critical` with corresponding municipal SLA deadlines (12h to 168h).

4. **Semantic Duplicate Detection**:
   - Cosine similarity vector search over complaint embeddings.
   - Detects recurring grievances in the same municipal ward, alerting administrators and linking citizen tickets to prevent duplicate work orders.

5. **Dynamic Department Recommendation**:
   - Database-driven mapping rules routing categories to appropriate civic bodies (Water Supply, Roads, Sanitation, Electricity, Street Lighting, Drainage).

6. **TPO / Administrative Command Center (`/admin`)**:
   - Comprehensive dashboard with live grievance metrics, SLA status, and recent intakes.
   - Triage console to review AI predictions, verify or override categories, and assign work orders to field officers.
   - Department SLA configuration and staff credential management.

7. **Field Staff Operations Desk (`/staff`)**:
   - Field officer task queue with SLA timers and quick status progression (`Assigned` → `In Progress` → `Resolved`) with action logs.

8. **Visual Analytics & AI Model Benchmark (`/admin/analytics`, `/admin/models`)**:
   - Chart.js dashboards: category bar charts, status doughnut charts, priority breakdowns, and 30-day intake trends.
   - Academic model evaluation suite: confusion matrices, per-class Precision/Recall/F1 tables, and an interactive live prediction sandbox for viva demonstrations.

---

## 👥 Demo Accounts (Pre-seeded)

You can use the one-click quick login buttons on the login page or enter credentials manually:

| Role | Email | Password | Scope |
|---|---|---|---|
| **Administrator / TPO** | `admin@gov.in` | `Admin@123` | Full portal oversight, complaint verification, department management |
| **Field Officer (Water Dept)** | `staff.water@gov.in` | `Staff@123` | Assigned work order queue, status updates |
| **Field Officer (Roads Dept)** | `staff.roads@gov.in` | `Staff@123` | Roads and infrastructure complaints queue |
| **Citizen** | `ramesh.sharma@gmail.com` | `Citizen@123` | Lodge grievances via AI chatbot, track complaints |
| **Citizen** | `priya.patel@gmail.com` | `Citizen@123` | Lodge grievances via AI chatbot, track complaints |

---

## 🏗️ Technology Architecture

- **Backend**: Python 3.11, FastAPI, SQLAlchemy ORM, SQLite / PostgreSQL ready, Pydantic v2, Jose JWT, Passlib Bcrypt.
- **Machine Learning**: Scikit-learn (CalibratedClassifierCV, LinearSVC, LogisticRegression, GradientBoostingClassifier, TfidfVectorizer), NumPy, Pandas, Joblib.
- **Frontend**: React 18, Vite, React Router v7, Vanilla CSS modern design system (glassmorphism, custom color variables, micro-animations), Lucide Icons, Chart.js, Axios.

---

## 🚀 Quickstart Guide

### 1. Backend Setup & Run

```bash
cd backend

# 1. Install dependencies
pip install -r requirements.txt

# 2. Train the ML models and generate evaluation metrics
python -m app.ml.training.train_classifier
python -m app.ml.training.train_priority
python -m app.ml.evaluation.evaluate_models

# 3. Seed database with departments, demo users, and sample complaints
python scripts/seed_database.py

# 4. Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

- Backend API: `http://localhost:8000`
- Interactive Swagger / OpenAPI Docs: `http://localhost:8000/docs`

### 2. Frontend Setup & Run

In a separate terminal:

```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Start Vite dev server
npm run dev
```

- Citizen Portal: `http://localhost:5173`

---

## 🧪 Running Automated Tests

```bash
cd backend
pytest tests/ -v
```

Tests verify:
- User registration, JWT token generation, and role authorization.
- Complaint creation, public ticket tracking, and status transitions.
- NLP classifier, priority predictor, and duplicate detection endpoints.
