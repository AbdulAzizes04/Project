import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database.session import init_db, SessionLocal
from app.api import investigations, videos, persons, analysis, evidence, timeline, reports, search, anpr

# Create storage directories
for d in ["uploads/videos", "uploads/images", "uploads/audio", "processed/clips", "processed/frames", "processed/reports"]:
    os.makedirs(d, exist_ok=True)

app = FastAPI(
    title="VisionTrace AI - Forensic Surveillance API",
    description="Intelligent Forensic Surveillance Platform for Smart Crime Investigation and Rapid Evidence Analysis",
    version="1.0.0"
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for video clips, snapshots, and reports
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/processed", StaticFiles(directory="processed"), name="processed")

# Include Routers
app.include_router(investigations.router)
app.include_router(videos.router)
app.include_router(persons.router)
app.include_router(analysis.router)
app.include_router(evidence.router)
app.include_router(timeline.router)
app.include_router(reports.router)
app.include_router(search.router)

@app.on_event("startup")
def on_startup():
    init_db()
    # Auto-seed demo case on startup if no investigations exist
    db = SessionLocal()
    try:
        from app.models import Investigation
        if db.query(Investigation).count() == 0:
            print("[VisionTrace AI] Empty database detected. Seeding initial forensic case...")
            from app.api.investigations import seed_demo_case
            seed_demo_case(db)
            print("[VisionTrace AI] Seed demo case initialized successfully.")
    except Exception as e:
        print(f"[VisionTrace AI] Startup seed notice: {e}")
    finally:
        db.close()

@app.get("/")
def root():
    return {
        "platform": "VisionTrace AI",
        "description": "AI-Assisted Forensic Surveillance Platform for Smart Crime Investigation",
        "status": "OPERATIONAL",
        "version": "1.0.0",
        "compliance": "AI-Assisted Analysis - Human Verification Required",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
