import logging
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import engine, Base
import app.models  # noqa: F401 - ensures all models registered

# Add ml directory to path for recommendation engine imports
ML_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "ml"))
if ML_DIR not in sys.path:
    sys.path.insert(0, ML_DIR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("career_ai.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified successfully.")
    except Exception as exc:
        logger.error(f"Error during database initialization: {exc}")
    yield
    logger.info("Application shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Explainable AI Framework for Personalized Career Recommendation Using Student Skill Analytics. "
        "Final-year B.Tech AIDS decision-support system featuring SHAP, LIME, and Skill-Gap analytics.\n\n"
        "⚠️ This platform provides career guidance only. It does NOT guarantee employment outcomes."
    ),
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register all routers
from app.routers import auth, student, portfolio, recommendations, admin

app.include_router(auth.router, prefix="/api")
app.include_router(student.router, prefix="/api")
app.include_router(portfolio.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An unexpected internal server error occurred.",
            "error_code": "INTERNAL_SERVER_ERROR",
            "detail": str(exc) if settings.DEBUG else None
        }
    )


@app.get("/", tags=["Health"])
async def root():
    return {
        "success": True,
        "message": "Explainable AI Career Recommendation System API is active.",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "notice": "This system provides career guidance only. It does NOT guarantee employment."
    }


@app.get("/health", tags=["Health"])
async def health_check():
    db_healthy = False
    dialect = "unknown"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_healthy = True
        dialect = engine.dialect.name
    except Exception as exc:
        logger.error(f"Health check database query failed: {exc}")

    return {
        "success": True,
        "status": "healthy" if db_healthy else "degraded",
        "database": {"connected": db_healthy, "dialect": dialect},
        "version": settings.VERSION
    }
