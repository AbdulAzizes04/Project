# Explainable AI Framework for Personalized Career Recommendation Using Student Skill Analytics

**Annamacharya Institute of Technology and Sciences (Autonomous)**  
*Department of Artificial Intelligence and Data Science*  
*Academic Year: 2026–2027*

---

## 1. Project Overview

Students in higher technical education frequently struggle to identify suitable career trajectories because their academic performance, technical skills, certifications, project experience, aptitude metrics, and domain interests are fragmented across disconnected sources. Traditional guidance systems rely on manual counseling or generic questionnaires that fail to uncover individual skill gaps or explain why a particular career is recommended.

This project delivers an **Explainable AI (XAI) Career Recommendation Decision-Support System** that analyzes comprehensive student skill analytics to recommend suitable industry career paths, providing mathematically grounded **SHAP** and **LIME** local feature attributions, automated skill-gap analysis, and personalized learning roadmaps.

> [!IMPORTANT]
> **Decision-Support Notice**: This platform is strictly a decision-support and career guidance tool. It does NOT claim to guarantee employment, placement, or hiring outcomes.

---

## 2. System Architecture

```
                 ┌────────────────────────────────────────────────────────┐
                 │                Next.js Modern Web App                  │
                 │   Student Dashboard / Admin Management / XAI Visuals   │
                 └──────────────────────────┬─────────────────────────────┘
                                            │ REST API (JSON / JWT)
                                            ▼
                 ┌────────────────────────────────────────────────────────┐
                 │                    FastAPI Backend                     │
                 │   Auth (RBAC) • Profiles • Recommendations • Endpoints │
                 └──────────────┬──────────────────────────┬──────────────┘
                                │                          │
                     SQLAlchemy ORM (pymysql)        Feature Vector
                                │                          │
                 ┌──────────────▼───────────┐   ┌──────────▼──────────────┐
                 │     MySQL Database       │   │    ML & XAI Engine      │
                 │   (career_ai_db / 23 tbl)│   │  Ensemble ML + Hybrid   │
                 └──────────────────────────┘   └──────────┬──────────────┘
                                                           │
                                                ┌──────────▼──────────────┐
                                                │      SHAP & LIME        │
                                                │ Local & Global Explains │
                                                └─────────────────────────┘
```

---

## 3. Technology Stack

- **Frontend**: Next.js (TypeScript), Tailwind CSS, shadcn/ui design patterns, Lucide React, Recharts.
- **Theme**: Clean White background (`#ffffff`), Light Blue primary accent (`#0284c7`), Neutral Slate secondary (`#64748b`), Emerald Green for positive/matching states, Crimson Red for missing/gap states.
- **Backend**: Python 3.11, FastAPI, Pydantic, SQLAlchemy, Uvicorn.
- **Machine Learning**: Scikit-learn, XGBoost, Pandas, NumPy, Joblib.
- **Explainable AI (XAI)**: SHAP (Tree/Kernel Explainer), LIME (Tabular Explainer).
- **Database**: MySQL 8.0 (primary) with resilient SQLite zero-config fallback.

---

## 4. Database Schema (23 Tables)

The database models are located in `backend/app/models/` and definitions in `database/schema.sql`:

1. `users` — Authentication & role-based access (`STUDENT`, `ADMIN`).
2. `student_profiles` — Personal information (name, phone, location, batch, branch, bio).
3. `academic_records` — 10th, 12th, CGPA, semester scores JSON, core subjects performance JSON.
4. `skills` — Centralized catalog of 35+ standardized industry skills.
5. `skill_aliases` — 47+ aliases for intelligent skill normalization (e.g. `JS` -> `JavaScript`).
6. `student_skills` — Student-acquired competencies with proficiency levels (`BEGINNER`, `INTERMEDIATE`, `ADVANCED`).
7. `certifications` & `student_certifications` — Credentials and verification links.
8. `projects` & `student_projects` — Technical projects, domains, complexities, and repositories.
9. `aptitude_scores` — Quantitative, logical reasoning, verbal, and technical aptitude scores.
10. `career_interests` — Preferred domains, career interests, preferred technologies, and soft skills.
11. `career_roles` — 7 target roles: Software Developer, Data Analyst, Data Scientist, AI/ML Engineer, Frontend Developer, Backend Developer, Cloud Engineer.
12. `career_skills` — Required vs preferred skills with importance weights (1.0 to 5.0).
13. `career_certifications` & `career_projects` — Expected qualifications per career path.
14. `career_recommendations` — Hybrid compatibility scores (0–100%) and multi-dimensional breakdown.
15. `recommendation_explanations` — Persisted SHAP/LIME attribution arrays and human-readable explanations.
16. `skill_gaps` — Gap status (`STRONG`, `MODERATE`, `MISSING`) and learning priority (`HIGH`, `MEDIUM`, `LOW`).
17. `learning_resources` — Curated courses, tutorials, and documentation links.
18. `student_progress` — Student-tracked milestones, courses, and skills with percentage completion.
19. `model_metrics` — ML offline evaluation metrics (Accuracy, Precision, Recall, F1, ROC-AUC, Confusion Matrix).
20. `audit_logs` — System-wide operational auditing.

---

## 5. Directory Structure

```
career-recommendation-ai/
│
├── frontend/                     # Next.js UI Application
│   ├── app/                      # Next.js App Router
│   ├── components/               # UI components, Recommendation Cards, Visualizations
│   ├── hooks/                    # Custom React hooks
│   ├── services/                 # API interaction services
│   ├── lib/                      # Utilities & HTTP client
│   ├── types/                    # TypeScript interfaces
│   └── public/                   # Static assets
│
├── backend/                      # FastAPI Application
│   ├── app/
│   │   ├── main.py               # FastAPI entrypoint, CORS, exception handling
│   │   ├── config.py             # Pydantic Settings
│   │   ├── database.py           # SQLAlchemy engine & session factory
│   │   ├── models/               # SQLAlchemy ORM models (23 tables)
│   │   ├── schemas/              # Pydantic validation schemas
│   │   ├── routers/              # API Route handlers
│   │   ├── services/             # Business & Recommendation logic
│   │   ├── middleware/           # Auth and error middleware
│   │   └── utils/                # Security & hashing helpers
│   ├── requirements.txt
│   └── .env
│
├── ml/                           # ML & Explainability Pipeline
│   ├── data/                     # Raw and synthetic datasets
│   ├── preprocessing/            # Skill normalization & vectorization
│   ├── training/                 # Offline model training & evaluation
│   ├── models/                   # Algorithm definitions
│   ├── recommendation/           # Hybrid recommendation engine
│   ├── explainability/           # SHAP & LIME explainers
│   ├── skill_gap/                # Gap classifier & priority scoring
│   └── artifacts/                # Serialized model (.joblib)
│
├── database/                     # Database Scripts
│   ├── schema.sql                # Complete MySQL 8.0 DDL
│   ├── seed.sql                  # Comprehensive seed data
│   └── init_db.py                # Automated multi-dialect database initializer
│
├── notebooks/                    # Academic Evaluation Notebooks
│   ├── data_analysis.ipynb
│   ├── model_training.ipynb
│   └── explainability.ipynb
│
└── README.md
```

---

## 6. How to Run (Phase 1 & Phase 2 Verified)

### Prerequisites
- Python 3.11+
- Node.js 18+

### Database Initialization
```powershell
cd "d:\projects\career project\career-recommendation-ai"
python database/init_db.py
```

### Running Backend API
```powershell
cd "d:\projects\career project\career-recommendation-ai\backend"
python -m uvicorn app.main:app --reload --port 8000
```
- API Documentation (Swagger UI): `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`
