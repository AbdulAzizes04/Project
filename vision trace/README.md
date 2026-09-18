# VisionTrace AI
### An Intelligent Forensic Surveillance Platform for Smart Crime Investigation and Rapid Evidence Analysis

> **B.Tech Final Year Project** — Artificial Intelligence & Data Science

---

## 🚀 Quick Start

### 1. Start the Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**

---

## 📁 Project Structure

```
visiontrace-ai/
├── frontend/           # React 18 + Vite + Tailwind CSS
│   └── src/
│       ├── components/ # Reusable UI components
│       ├── pages/      # 6 main pages
│       └── services/   # API client
│
├── backend/            # FastAPI + Python 3.11
│   ├── api/            # REST API routes
│   ├── services/       # AI pipeline services
│   ├── database/       # SQLAlchemy + SQLite
│   └── reports/        # PDF & DOCX generators
│
└── uploads/            # Uploaded CCTV videos & reference images
```

---

## 🧭 Application Modules

| Module | Description |
|--------|-------------|
| **Dashboard & Analytics** | Live stats, charts, evidence timeline |
| **Search & Gait Pipeline** | Upload footage, run AI analysis |
| **AI Forensic Chatbot** | NL query engine over case database |
| **CCTV Video Player** | Footage playback with AI overlays |
| **SQLite Case Logs** | Investigation management |
| **About** | Project info, tech stack, pipeline |

---

## 🤖 AI Pipeline

```
CCTV Video
    ↓
Frame Extraction (OpenCV)
    ↓
YOLOv8 Person Detection
    ↓
ByteTrack Multi-Object Tracking
    ↓
Person Re-Identification (HSV + ResNet50)
    ↓
Gait Analysis (trajectory patterns)
    ↓
Multi-Modal Score Fusion
    ↓
Evidence Timeline → SQLite → PDF/DOCX Report
```

---

## 🛠 Technology Stack

### Frontend
- React 18, Vite, Tailwind CSS
- React Router DOM, Recharts, Lucide React, Axios

### Backend
- Python 3.11, FastAPI, Uvicorn
- SQLAlchemy, SQLite

### AI / Computer Vision
- Ultralytics YOLOv8 (person detection)
- ByteTrack via supervision (multi-object tracking)
- OpenCV (video processing, frame extraction)
- PyTorch + ResNet50 (person re-identification)
- SciPy, Scikit-learn (feature processing)

### Reports
- ReportLab (PDF), python-docx (DOCX)

---

## 🎭 Demo Mode

Click any **1-Click Demo Scenario** on the Search & Gait Pipeline page to run a simulated investigation without needing a real video file.

> Demo results are clearly labelled as **DEMO / SIMULATED DATA**

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/cases/create` | Create investigation case |
| `GET` | `/api/cases` | List all cases |
| `POST` | `/api/analysis/upload` | Upload video + reference image |
| `POST` | `/api/analysis/run` | Start AI pipeline |
| `GET` | `/api/analysis/{id}/status` | Poll processing status |
| `POST` | `/api/chat` | Ask forensic questions |
| `GET` | `/api/reports/{id}/pdf` | Download PDF report |
| `GET` | `/api/reports/{id}/docx` | Download DOCX report |

---

## ⚠️ Disclaimer

This is an **academic prototype** for educational purposes.  
AI confidence scores are computational estimates — **NOT legally conclusive**.  
Results must be reviewed by a qualified forensic professional before any official use.

---

*Built with ❤️ for B.Tech AI & Data Science Final Year Project*
