from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.models import TimelineEvent
from app.schemas import TimelineEventResponse

router = APIRouter(prefix="/api/timeline", tags=["Activity & Movement Timeline"])

@router.get("/{investigation_id}", response_model=List[TimelineEventResponse])
def get_investigation_timeline(investigation_id: str, db: Session = Depends(get_db)):
    events = db.query(TimelineEvent).filter(TimelineEvent.investigation_id == investigation_id).order_by(TimelineEvent.timestamp.asc()).all()
    return events
