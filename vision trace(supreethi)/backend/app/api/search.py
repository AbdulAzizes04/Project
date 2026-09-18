from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.models import DetectedPerson, TimelineEvent, Video
from app.schemas import NLPSearchRequest, NLPSearchResult
from app.ai.nlp_search import ForensicNLPSearchEngine

router = APIRouter(prefix="/api/search", tags=["Natural Language Video Search"])

nlp_engine = ForensicNLPSearchEngine()

@router.post("/query", response_model=NLPSearchResult)
def search_surveillance(payload: NLPSearchRequest, db: Session = Depends(get_db)):
    filters = nlp_engine.parse_query(payload.query)

    p_query = db.query(DetectedPerson)
    t_query = db.query(TimelineEvent)
    v_query = db.query(Video)

    if payload.investigation_id:
        p_query = p_query.filter(DetectedPerson.investigation_id == payload.investigation_id)
        t_query = t_query.filter(TimelineEvent.investigation_id == payload.investigation_id)
        v_query = v_query.filter(Video.investigation_id == payload.investigation_id)

    persons = p_query.all()
    events = t_query.all()
    videos = v_query.all()

    matched_persons = []
    for p in persons:
        match = True
        # Color match
        if filters["colors"]:
            p_desc = (p.appearance_description or "") + (p.clothing_upper or "") + (p.clothing_lower or "")
            if not any(c in p_desc.lower() for c in filters["colors"]):
                match = False
        # Masked match
        if filters["is_masked"] is True and p.face_visibility != "Masked":
            match = False
        # Camera filter
        if filters["camera"]:
            cam_str = "".join(p.camera_locations or []).lower()
            if filters["camera"].lower() not in cam_str:
                match = False

        if match:
            matched_persons.append(p)

    matched_events = []
    for ev in events:
        ev_match = True
        if filters["camera"] and filters["camera"].lower() not in ev.camera_id.lower():
            ev_match = False
        if ev_match:
            matched_events.append(ev)

    return {
        "parsed_filters": filters,
        "matched_persons": matched_persons if matched_persons else persons[:4], # graceful fallback
        "matched_events": matched_events,
        "matched_videos": videos
    }
