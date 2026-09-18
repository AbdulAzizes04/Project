"""Analytics API routes — charts, dashboard, and AI model metrics."""
from fastapi import APIRouter, Depends, Query
from app.core.dependencies import DbSession, require_role
from app.services.analytics_service import analytics_service

router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"],
    dependencies=[Depends(require_role("admin", "staff"))],
)


@router.get("/overview")
@router.get("/dashboard")
def dashboard_stats(db: DbSession):
    stats = analytics_service.get_dashboard_stats(db)
    return {"success": True, "data": stats, "stats": stats}


@router.get("/categories")
def complaints_by_category(db: DbSession):
    data = analytics_service.complaints_by_category(db)
    return {"success": True, "data": data}


@router.get("/priorities")
def complaints_by_priority(db: DbSession):
    data = analytics_service.complaints_by_priority(db)
    return {"success": True, "data": data}


@router.get("/status")
def complaints_by_status(db: DbSession):
    data = analytics_service.complaints_by_status(db)
    return {"success": True, "data": data}


@router.get("/departments")
def complaints_by_department(db: DbSession):
    data = analytics_service.complaints_by_department(db)
    return {"success": True, "data": data}


@router.get("/timeline")
def complaints_timeline(db: DbSession, days: int = Query(30, ge=7, le=365)):
    data = analytics_service.complaints_timeline(db, days)
    return {"success": True, "data": data}


@router.get("/models")
def model_metrics(db: DbSession):
    """AI model performance metrics — sourced from actual evaluations stored in DB."""
    data = analytics_service.get_model_metrics(db)
    return {"success": True, "data": data}
