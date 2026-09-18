"""
VisionTrace AI — Chatbot API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from database import models, schemas
from services.evidence_agent import EvidenceAgent
from datetime import datetime, timezone

router = APIRouter(prefix="/api/chat", tags=["Chatbot"])
agent = EvidenceAgent()


@router.post("", response_model=schemas.ChatResponse)
def chat(req: schemas.ChatRequest, db: Session = Depends(get_db)):
    result = agent.answer(req.question, db, req.case_id)

    # Persist conversation
    history = models.ChatHistory(
        case_id=req.case_id,
        question=req.question,
        answer=result["answer"],
        timestamp=datetime.now(timezone.utc),
    )
    db.add(history)
    db.commit()

    return schemas.ChatResponse(answer=result["answer"], sources=result.get("sources", []))


@router.get("/history")
def get_history(case_id: int = None, limit: int = 20, db: Session = Depends(get_db)):
    q = db.query(models.ChatHistory)
    if case_id:
        q = q.filter(models.ChatHistory.case_id == case_id)
    return q.order_by(models.ChatHistory.timestamp.desc()).limit(limit).all()
