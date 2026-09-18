# VisionTrace AI

### *An Intelligent Forensic Surveillance Platform for Smart Crime Investigation and Rapid Evidence Analysis*

VisionTrace AI is a modern forensic surveillance web application engineered to assist law enforcement detectives, intelligence analysts, and security operations centers in organizing CCTV video feeds, identifying and tracking potential persons of interest across multiple camera sectors, generating chronological movement timelines, and producing court-admissible forensic dossiers.

---

## Legal & Forensic Compliance Directive

> [!IMPORTANT]
> **AI-Assisted Investigation Disclaimer**: VisionTrace AI is strictly designed as an **AI-Assisted Forensic Tool**. The system **NEVER** claims that the artificial intelligence definitively proves a suspect's identity or establishes legal guilt.
> All outputs are explicitly marked as:
> - **Potential Match**
> - **Person of Interest (POI) Candidate**
> - **Similarity Score & Kinematic Cadence**
> - **Human Verification Required**
> 
> **Masked Suspect Principle**: When a subject's facial biometrics are obscured or masked by a balaclava, scarf, or medical mask, the system **never hallucinates or generates a synthetic face**. Instead, it automatically switches over to the **Alternative Forensic Pipeline**: Body Silhouette aspect ratio, clothing color histograms, and **MediaPipe Joint Kinematic Gait Analysis**.

---

## Primary Application Workflow

```text
Dashboard & Surveillance Hub
        ↓
Create New Investigation (5-Step Wizard)
        ↓
Enter Incident Metadata (Case ID, Jurisdiction, Date/Time)
        ↓
Upload CCTV Video Streams (Multi-Camera Ingestion & Resolution Calibration)
        ↓
Upload Reference Images (Suspect / Victim / Both / Unsupervised Discovery)
        ↓
AI Processing Pipeline (Live Status HUD)
        ↓
[YOLOv8 Detection] → [ByteTrack Persistent Tracking] → [Deep Re-ID Embeddings]
        ↓
[Face Occlusion & Mask Detector] → [MediaPipe Kinematic Gait Profiler]
        ↓
Generate Candidate Person of Interest Profiles (AI Relevance Scores)
        ↓
Extract Suspect Activity Video Clips (Person_Of_Interest_07_Evidence.mp4)
        ↓
Multi-Camera Chronological Movement Timeline
        ↓
Forensic Evidence Viewer (Slow-Mo, Frame Stepping, Bounding Boxes, CLAHE Low-Light Slider)
        ↓
Generate Forensic PDF Investigation Report (Court Sign-off & Verification)
```

---

## Technology Stack

### Frontend
- **Framework**: Next.js 16 (App Router, TypeScript, React 19)
- **Styling**: Tailwind CSS, Custom Surveillance HUD CSS & Glassmorphism
- **Icons**: Lucide React
- **Animations**: Framer Motion & CSS Radar Keyframes
- **Analytics & Data Vis**: Recharts (Hourly activity, threat pie charts, cadence meters)

### Backend
- **Framework**: Python 3.11+ & FastAPI
- **Database**: Relational SQLite default (`sqlite:///./visiontrace.db`) with seamless PostgreSQL support via `DATABASE_URL`
- **ORM & Validation**: SQLAlchemy 2.0 & Pydantic v2
- **PDF Generation**: ReportLab (official legal layout with tables, headers, and disclaimers)

### Computer Vision & Forensic AI
- **Object Detection**: Ultralytics YOLOv8 (`yolov8n.pt`) with OpenCV HOG fallback
- **Object Tracking**: Centroid & IoU Persistent Trajectory Tracker (maintains Track IDs across camera jumps)
- **Person Re-ID**: ResNet-18 Deep Feature Extractor & Spatial Color Pyramid Cosine Matching
- **Mask Detection**: Face bounding box occlusion analyzer with automatic alternative gait trigger
- **Gait Analysis**: MediaPipe Pose kinematic joint extraction (Speed, Step Cadence, Arm Swing, Torso Lean, assigned signature e.g. `GAIT-007`)
- **Low-Light Enhancement**: OpenCV LAB-space CLAHE (Contrast Limited Adaptive Histogram Equalization) + Non-linear Gamma Expansion + Bilateral Edge Denoising
- **ANPR**: License Plate localization + EasyOCR character reader
- **NLP Query Parser**: Structured natural language metadata search engine

---

## Monorepo Architecture

```text
visiontrace-ai/
├── frontend/                     # Next.js App Router frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx          # Main dashboard & live intelligence overview
│   │   │   ├── dashboard/        # Dashboard view
│   │   │   ├── investigations/   # Case archive directory
│   │   │   │   ├── new/          # 5-step Multi-step Investigation Wizard
│   │   │   │   └── [id]/         # Investigation Dossier & POI Explorer
│   │   │   ├── evidence/         # Forensic Evidence Viewer & Low-Light CLAHE Slider
│   │   │   ├── search/           # Natural Language Surveillance Search
│   │   │   ├── anpr/             # Vehicle & License Plate Recognition Module
│   │   │   └── reports/          # Forensic Reports & Printable PDF Export
│   │   ├── components/
│   │   │   ├── dashboard/        # Dashboard stats, charts, and activity streams
│   │   │   ├── layout/           # Navbar, DisclaimerBanner, Footer
│   │   │   └── ui/               # Reusable surveillance UI components
│   │   └── lib/
│   │       ├── api.ts            # REST API client with fallback resilience
│   │       └── types.ts          # TypeScript interfaces
│   └── package.json
│
├── backend/                      # Python FastAPI application
│   ├── app/
│   │   ├── main.py               # Application entrypoint & static mount
│   │   ├── database/             # SQLAlchemy engine & session
│   │   ├── models/               # Relational database models
│   │   ├── schemas/              # Pydantic request/response models
│   │   ├── api/                  # REST routers (investigations, videos, persons, reports...)
│   │   ├── ai/                   # Modular CV engines:
│   │   │   ├── detection.py      # YOLOv8 person & vehicle detector
│   │   │   ├── tracking.py       # Trajectory & track ID persistence
│   │   │   ├── reid.py           # Feature extraction & reference cosine similarity
│   │   │   ├── mask_detector.py  # Face occlusion & mask trigger
│   │   │   ├── gait_analyzer.py  # MediaPipe joint kinematics & gait signatures
│   │   │   ├── enhancement.py    # CLAHE & gamma low-light enhancer
│   │   │   ├── anpr.py           # License plate OCR recognizer
│   │   │   └── nlp_search.py     # Natural language query interpreter
│   │   └── services/
│   │       ├── pipeline.py       # Asynchronous master forensic pipeline
│   │       └── report_generator.py # Court-admissible PDF generator
│   ├── requirements.txt
│   └── .env.example
│
├── uploads/                      # Storage for CCTV videos, reference photos, audio
├── processed/                    # Storage for crops, evidence clips, and generated PDFs
└── README.md
```

---

## Quick Start Guide

### 1. Start the Backend API
```bash
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Health & Documentation: `http://127.0.0.1:8000/docs`
- On startup, the database automatically seeds a complete demonstration case (`CASE-2026-089: Armed Jewelry Vault Heist`).

### 2. Start the Frontend Application
```bash
cd frontend
npm run dev -- -p 3000
```
- Access the web application: `http://localhost:3000`

---

## Live Demonstration Walkthrough (For Project Viva / Showcase)

1. **Dashboard & Surveillance Grid (`/dashboard`)**:
   - Inspect active case metrics, 1080p camera counts, and Recharts hourly activity stream.
   - Click the **"Load Viva Demo"** button on the top navigation bar at any time to re-seed realistic forensic data.
2. **Investigation Creation Wizard (`/investigations/new`)**:
   - Follow the 5-step wizard: Enter incident metadata, inspect calibrated camera streams, choose reference image mode, and watch the real-time animated AI pipeline checklist complete.
3. **Person of Interest & Gait Kinematics (`/investigations/[id]`)**:
   - Observe **Candidate #07** flagged with 91% AI Relevance.
   - Note the **Face Visibility: MASKED** warning alert and the activated **Alternative Gait Pipeline**.
   - Review the **MediaPipe Joint Kinematics Gait Profile** (`GAIT-007`, walking speed, arm swing restriction, forward lean).
   - Click **"GENERATE SUSPECT ACTIVITY VIDEO"** to compile `Person_Of_Interest_07_Evidence.mp4`.
4. **Forensic Evidence Player (`/evidence`)**:
   - Test **Slow Motion (0.25x, 0.5x, 1x)** and **Frame-by-Frame Stepping**.
   - Toggle the **"Low-Light CLAHE Slider"** to interactively compare raw night-vision CCTV vs. histogram-equalized footage.
   - Flag and record new timestamped **Evidence Markers**.
5. **Natural Language Search (`/search`)**:
   - Query: *"Show persons wearing black clothing"* or *"Find a person entering after 7 PM near Camera 01"*.
   - Inspect parsed filter pills and matched suspect crops.
6. **ANPR Scanner (`/anpr`)**:
   - Review optical character recognition plates, vehicle classifications, and camera timestamps.
7. **Forensic Report & PDF Export (`/reports`)**:
   - View official investigation dossier with case information, candidate analysis, movement timeline table, and human investigator sign-off block.
   - Click **"EXPORT FORENSIC PDF"** or **"Browser Print"**.
