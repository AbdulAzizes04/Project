# BuildVerse AI — AI-Powered Digital Twin & Construction Platform

BuildVerse AI is an end-to-end intelligent Digital Twin and construction site monitoring application. It assists users from initial 2D vector floor plan design to AI 12-phase schedule generation, daily media progress evaluation, 3D Digital Twin model sync, ReportLab PDF export, and executive KPI analytics.

## Design Theme System
- **Background**: White (`#FFFFFF`) / Light Slate (`#F8FAFC`)
- **Primary Color**: Rich Cyan (`#0891B2`)
- **Secondary Color / Accents**: Light / Semi-Cyan (`#E0F2FE` / `#06B6D4` / `#A5F3FC`)
- **Text Color**: Dark Slate / Black (`#0F172A`) for maximum contrast and readability.

---

## Directory Structure

```
buildverse-ai/
├── app.py                      # Main Streamlit entry point
├── requirements.txt            # Python dependencies
├── config.py                   # Global configuration & color theme tokens
├── README.md                   # Documentation
├── assets/
│   ├── css/style.css           # Custom CSS design system
│   ├── js/
│   ├── icons/
│   ├── images/
│   └── videos/
├── database/
│   ├── schema.sql              # Database DDL schema
│   ├── models.py              # Pydantic data models
│   ├── db.py                  # Connection & CRUD database operations
│   └── migrations/
├── uploads/                    # Storage for site images, videos, drone footage & reports
├── ai/
│   ├── planner/                # 2D/3D floor planning & dimension validation
│   ├── construction/           # Schedule, cost, labor & material estimation
│   ├── vision/                 # OpenCV & YOLO computer vision site progress detector
│   ├── llm/                    # AI recommendation engine & report summaries
│   └── digital_twin/           # 3D Digital Twin mesh generator & live sync
├── visualization/              # Cyan Plotly charts, Gantt charts & S-curve graphs
├── rag/                        # Vector store for building codes
├── api/                        # Unified API endpoints for planning, monitoring & PDF reports
└── pages/                      # Multi-page Streamlit views (01 Home to 08 Dashboard)
```

---

## Installation & Running Locally

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

3. Open your browser at `http://localhost:8501`.
