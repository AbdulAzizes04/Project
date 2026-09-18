"""Pydantic schemas for AI prediction results."""
from typing import Optional, List
from pydantic import BaseModel


class ClassificationResult(BaseModel):
    category: str
    confidence: float
    all_scores: Optional[dict] = None
    low_confidence: bool = False


class PriorityResult(BaseModel):
    priority: str
    confidence: float
    all_scores: Optional[dict] = None
    rule_based_fallback: bool = False


class DuplicateResult(BaseModel):
    is_duplicate: bool
    similarity: float
    matched_complaint_id: Optional[str] = None
    matched_complaint_number: Optional[str] = None
    matched_description: Optional[str] = None
    matched_location: Optional[str] = None
    matched_status: Optional[str] = None


class AnalysisResult(BaseModel):
    """Full AI pipeline result — classification + priority + duplicate + department."""
    classification: ClassificationResult
    priority: PriorityResult
    duplicate: DuplicateResult
    recommended_department_id: Optional[str] = None
    recommended_department_name: Optional[str] = None
    overall_confidence: float


class AnalysisRequest(BaseModel):
    text: str
    location: Optional[str] = None
    duration: Optional[str] = None
    severity: Optional[str] = None


class ClassifyRequest(BaseModel):
    text: str


class PriorityRequest(BaseModel):
    text: str
    category: Optional[str] = None
    severity: Optional[str] = None
    duration: Optional[str] = None


class DuplicateRequest(BaseModel):
    text: str
    location: Optional[str] = None
    exclude_complaint_id: Optional[str] = None
