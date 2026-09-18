"""
FastAPI Application Entry Point.
Configures middleware, CORS, routers, startup/shutdown events.
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app.core.config import settings
from app.core.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database: {settings.DATABASE_URL}")

    # Create database tables
    create_tables()
    logger.info("Database tables created/verified.")

    # Create upload directory
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("app/ml/models", exist_ok=True)

    logger.info("Application startup complete.")
    yield

    logger.info("Application shutdown.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## AI-Based Intelligent Public Grievance Redressal System

A production-grade system for automated complaint classification, priority prediction,
duplicate detection, and department routing using NLP and Machine Learning.

### Features
- **Conversational AI Chatbot** — guided complaint registration
- **Complaint Classification** — TF-IDF + LinearSVC (6 categories)
- **Priority Prediction** — Gradient Boosting with engineered features
- **Duplicate Detection** — Sentence Transformers + cosine similarity
- **Department Routing** — DB-driven category-to-department mapping
- **Status Workflow** — SUBMITTED → AI_ANALYZED → VERIFIED → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED
- **Role-Based Access** — Citizen / Admin / Staff

### Authentication
Use Bearer token obtained from `/api/auth/login`.
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/openapi.json",
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Global Exception Handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc} | Path: {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An unexpected error occurred. Please try again.",
            "error_code": "INTERNAL_SERVER_ERROR",
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "message": str(exc),
            "error_code": "VALIDATION_ERROR",
        },
    )

# ─── Include Routers ────────────────────────────────────────────────────────────
from app.api.auth import router as auth_router
from app.api.chatbot import router as chatbot_router
from app.api.complaints import router as complaints_router, citizen_router
from app.api.admin import router as admin_router
from app.api.departments import router as departments_router
from app.api.analytics import router as analytics_router
from app.api.ai import router as ai_router
from app.api.notifications import router as notifications_router

app.include_router(auth_router)
app.include_router(chatbot_router)
app.include_router(citizen_router)
app.include_router(complaints_router)
app.include_router(admin_router)
app.include_router(departments_router)
app.include_router(analytics_router)
app.include_router(ai_router)
app.include_router(notifications_router)

# Alias for /api/users
from app.api.admin import list_users
app.add_api_route("/api/users", list_users, methods=["GET"], tags=["Users"])

@app.get("/openapi.json", include_in_schema=False)
def openapi_alias():
    return app.openapi()

# Serve uploaded files
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/", tags=["Health"])
def root():
    return {
        "success": True,
        "message": f"{settings.APP_NAME} is running.",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }
