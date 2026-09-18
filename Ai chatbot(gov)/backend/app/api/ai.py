"""Direct AI endpoint — for testing classification, priority, and duplicate detection."""
from fastapi import APIRouter, Depends
from app.core.dependencies import CurrentUser, DbSession
from app.schemas.prediction import (
    ClassifyRequest, PriorityRequest, DuplicateRequest, AnalysisRequest,
    ClassificationResult, PriorityResult, DuplicateResult, AnalysisResult,
)
from app.services.classification_service import classification_service
from app.services.priority_service import priority_service
from app.services.duplicate_service import duplicate_service
from app.services.department_service import department_service

router = APIRouter(prefix="/api/ai", tags=["AI"])


@router.post("/classify", response_model=ClassificationResult)
def classify_complaint(request: ClassifyRequest, current_user: CurrentUser):
    """Classify complaint text into a category."""
    result = classification_service.classify(request.text)
    return ClassificationResult(
        category=result["category"],
        confidence=result["confidence"],
        all_scores=result.get("all_scores"),
        low_confidence=result.get("low_confidence", False),
    )


@router.post("/priority", response_model=PriorityResult)
def predict_priority(request: PriorityRequest, current_user: CurrentUser):
    """Predict complaint priority."""
    result = priority_service.predict_priority(
        text=request.text,
        category=request.category or "",
        severity=request.severity or "",
        duration=request.duration or "",
    )
    return PriorityResult(
        priority=result["priority"],
        confidence=result["confidence"],
        all_scores=result.get("all_scores"),
        rule_based_fallback=result.get("rule_based_fallback", False),
    )


@router.post("/duplicate", response_model=DuplicateResult)
def check_duplicate(request: DuplicateRequest, current_user: CurrentUser, db: DbSession):
    """Check if a complaint text is a duplicate of existing complaints."""
    result = duplicate_service.check_duplicate(
        new_text=request.text,
        db=db,
        location=request.location,
        exclude_complaint_id=request.exclude_complaint_id,
    )
    return DuplicateResult(**result)


@router.post("/analyze", response_model=AnalysisResult)
def full_analysis(request: AnalysisRequest, current_user: CurrentUser, db: DbSession):
    """Run the full AI pipeline: classify + priority + duplicate + department recommendation."""
    full_text = f"{request.text} {request.location or ''} {request.duration or ''} {request.severity or ''}".strip()

    classification = classification_service.classify(request.text)
    priority = priority_service.predict_priority(
        text=request.text,
        category=classification["category"],
        severity=request.severity or "",
        duration=request.duration or "",
    )
    duplicate = duplicate_service.check_duplicate(new_text=full_text, db=db)
    dept_id, dept_name = department_service.recommend_department(
        classification["category"], db
    )

    overall_confidence = round(
        classification["confidence"] * 0.6 + priority["confidence"] * 0.4, 4
    )

    return AnalysisResult(
        classification=ClassificationResult(
            category=classification["category"],
            confidence=classification["confidence"],
            all_scores=classification.get("all_scores"),
            low_confidence=classification.get("low_confidence", False),
        ),
        priority=PriorityResult(
            priority=priority["priority"],
            confidence=priority["confidence"],
            all_scores=priority.get("all_scores"),
            rule_based_fallback=priority.get("rule_based_fallback", False),
        ),
        duplicate=DuplicateResult(**duplicate),
        recommended_department_id=dept_id,
        recommended_department_name=dept_name,
        overall_confidence=overall_confidence,
    )


@router.get("/status")
def ai_status(current_user: CurrentUser):
    """Check availability of AI models."""
    return {
        "success": True,
        "classification_model": classification_service.is_ready(),
        "priority_model": priority_service.is_ready(),
        "sentence_transformer": duplicate_service.is_ready(),
        "message": (
            "All AI models ready."
            if all([
                classification_service.is_ready(),
                priority_service.is_ready(),
                duplicate_service.is_ready()
            ])
            else "Some models not ready. Run training scripts first."
        ),
    }
