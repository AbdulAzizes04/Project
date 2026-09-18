"""
VisionTrace AI — Evidence Agent (AI Forensic Chatbot Engine)
Database-grounded natural language Q&A for forensic investigation queries.
No external LLM API required. Answers are derived strictly from SQLite data.
"""
import re
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from database import models


class EvidenceAgent:
    """
    Rule-based forensic question answering engine.
    Parses natural language and retrieves structured answers from the DB.
    """

    # ── Intent patterns ────────────────────────────────────────────────────────
    PATTERNS = [
        (r"track\s*(\d+).*(first|appear|entry|enter|seen)", "track_entry"),
        (r"(when|time|timestamp).*(helmet|cover|remov)", "helmet_event"),
        (r"track\s*(\d+).*(activity|activit|summar|report|behav)", "track_summary"),
        (r"(how many|count|total).*(person|people|track|detect)", "count_persons"),
        (r"(highest|best|top|most).*(confidence|score|match)", "top_match"),
        (r"track\s*(\d+).*(exit|left|last|gone)", "track_exit"),
        (r"(evidence|timeline|event)", "timeline"),
        (r"(confidence|score|rating)", "overall_confidence"),
        (r"(case|investigation|summar)", "case_summary"),
        (r"(green|shirt|jacket|cloth|wear)", "clothing_query"),
    ]

    def answer(
        self,
        question: str,
        db: Session,
        case_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        q = question.lower().strip()

        # Detect intent
        intent, match = self._detect_intent(q)

        try:
            if intent == "track_entry":
                tid = int(match.group(1)) if match and match.group(1) else None
                return self._track_entry(db, case_id, tid)
            elif intent == "helmet_event":
                return self._helmet_event(db, case_id)
            elif intent == "track_summary":
                tid = int(match.group(1)) if match and match.group(1) else None
                return self._track_summary(db, case_id, tid)
            elif intent == "count_persons":
                return self._count_persons(db, case_id)
            elif intent == "top_match":
                return self._top_match(db, case_id)
            elif intent == "track_exit":
                tid = int(match.group(1)) if match and match.group(1) else None
                return self._track_exit(db, case_id, tid)
            elif intent == "timeline":
                return self._timeline(db, case_id)
            elif intent == "overall_confidence":
                return self._overall_confidence(db, case_id)
            elif intent == "case_summary":
                return self._case_summary(db, case_id)
            elif intent == "clothing_query":
                return self._clothing_query(db, case_id)
            else:
                return self._fallback(db, case_id, question)
        except Exception as e:
            return {
                "answer": f"⚠️ I encountered an error retrieving that information: {str(e)}",
                "sources": [],
            }

    def _detect_intent(self, q: str):
        for pattern, intent in self.PATTERNS:
            m = re.search(pattern, q)
            if m:
                return intent, m
        return "unknown", None

    def _get_case(self, db: Session, case_id: Optional[int]) -> Optional[models.Case]:
        if case_id:
            return db.query(models.Case).filter(models.Case.id == case_id).first()
        return db.query(models.Case).order_by(models.Case.id.desc()).first()

    def _fmt_time(self, secs: float) -> str:
        m, s = divmod(int(secs), 60)
        return f"{m:02d}:{s:02d}"

    # ── Intent handlers ────────────────────────────────────────────────────────

    def _track_entry(self, db, case_id, tid):
        track = self._find_track(db, case_id, tid)
        if not track:
            return {"answer": f"Track {tid or 'N/A'} was not found in the current investigation.", "sources": []}
        t = self._fmt_time(track.first_seen)
        return {
            "answer": (
                f"🕐 **Track {track.track_number}** first appeared in the monitored area at **{t}**.\n\n"
                f"It remained visible for **{track.duration:.1f} seconds** "
                f"across **{track.appearance_count}** detection frames, "
                f"with an average detection confidence of **{track.avg_confidence:.1%}**."
            ),
            "sources": [f"Track #{track.track_number}", f"Case ID {case_id or 'latest'}"],
        }

    def _track_exit(self, db, case_id, tid):
        track = self._find_track(db, case_id, tid)
        if not track:
            return {"answer": f"Track {tid or 'N/A'} was not found.", "sources": []}
        t = self._fmt_time(track.last_seen)
        return {
            "answer": (
                f"🚪 **Track {track.track_number}** was last detected at **{t}** "
                f"after being tracked for **{track.duration:.1f}s** total."
            ),
            "sources": [f"Track #{track.track_number}"],
        }

    def _helmet_event(self, db, case_id):
        case = self._get_case(db, case_id)
        ev = (
            db.query(models.Evidence)
            .filter(
                models.Evidence.case_id == (case.id if case else 0),
                models.Evidence.event_type == "helmet_removal",
            )
            .first()
        )
        if ev:
            return {
                "answer": (
                    f"🪖 A **helmet/head covering removal** event was detected at "
                    f"**{self._fmt_time(ev.timestamp)}** (Track {ev.track_id}).\n\n"
                    f"Detection confidence: **{ev.confidence:.1%}**. "
                    f"Shortly after, facial features became partially visible, "
                    f"enabling stronger biometric comparison."
                ),
                "sources": ["Evidence timeline", f"Event ID {ev.id}"],
            }
        return {
            "answer": "No helmet removal event was detected in this investigation.",
            "sources": [],
        }

    def _track_summary(self, db, case_id, tid):
        track = self._find_track(db, case_id, tid)
        if not track:
            return {"answer": f"Track {tid or 'N/A'} not found.", "sources": []}

        case = self._get_case(db, case_id)
        ar = (
            db.query(models.AnalysisResult)
            .filter(models.AnalysisResult.track_id == track.id)
            .first()
        )
        events = (
            db.query(models.Evidence)
            .filter(models.Evidence.track_id == track.track_number)
            .order_by(models.Evidence.timestamp)
            .all()
        ) if case else []

        lines = [
            f"📋 **Track {track.track_number} — Full Behavioral Summary**\n",
            f"- **First seen:** {self._fmt_time(track.first_seen)}",
            f"- **Last seen:** {self._fmt_time(track.last_seen)}",
            f"- **Duration:** {track.duration:.1f}s",
            f"- **Detection frames:** {track.appearance_count}",
            f"- **Avg confidence:** {track.avg_confidence:.1%}",
        ]
        if ar:
            lines += [
                f"\n🧠 **AI Analysis Scores:**",
                f"- Re-ID similarity: **{ar.reid_score:.1%}**",
                f"- Gait similarity: **{ar.gait_score:.1%}**",
                f"- Clothing match: **{ar.clothing_score:.1%}**",
                f"- **Overall confidence: {ar.final_score:.1%}** → **{ar.evidence_rating}**",
            ]
        if events:
            lines.append("\n🗓️ **Timeline events:**")
            for ev in events[:6]:
                lines.append(f"  • {self._fmt_time(ev.timestamp)} — {ev.description}")

        return {"answer": "\n".join(lines), "sources": [f"Track {track.track_number}", "Analysis DB"]}

    def _count_persons(self, db, case_id):
        case = self._get_case(db, case_id)
        if not case:
            return {"answer": "No active investigation found.", "sources": []}
        count = db.query(models.Track).filter(models.Track.case_id == case.id).count()
        return {
            "answer": (
                f"👥 A total of **{count} unique individuals** were tracked in this investigation "
                f"({case.case_name}). "
                f"Of these, **{case.matches_found}** were identified as potential suspect matches "
                f"above the configured similarity threshold."
            ),
            "sources": [f"Case: {case.case_name}", "Tracking DB"],
        }

    def _top_match(self, db, case_id):
        case = self._get_case(db, case_id)
        if not case:
            return {"answer": "No active investigation.", "sources": []}
        ar = (
            db.query(models.AnalysisResult)
            .filter(models.AnalysisResult.case_id == case.id)
            .order_by(models.AnalysisResult.final_score.desc())
            .first()
        )
        if not ar:
            return {"answer": "No analysis results found.", "sources": []}
        track = db.query(models.Track).filter(models.Track.id == ar.track_id).first()
        tid = track.track_number if track else ar.track_id
        return {
            "answer": (
                f"🏆 The highest confidence match is **Track {tid}** with an overall score of "
                f"**{ar.final_score:.1%}** (Evidence Rating: **{ar.evidence_rating}**).\n\n"
                f"- Re-ID: {ar.reid_score:.1%}  |  Gait: {ar.gait_score:.1%}  "
                f"|  Clothing: {ar.clothing_score:.1%}"
            ),
            "sources": [f"Track {tid}", "Analysis results DB"],
        }

    def _timeline(self, db, case_id):
        case = self._get_case(db, case_id)
        if not case:
            return {"answer": "No active investigation.", "sources": []}
        events = (
            db.query(models.Evidence)
            .filter(models.Evidence.case_id == case.id)
            .order_by(models.Evidence.timestamp)
            .limit(10)
            .all()
        )
        if not events:
            return {"answer": "No evidence timeline events found.", "sources": []}
        lines = ["🗓️ **Evidence Timeline:**\n"]
        for ev in events:
            lines.append(f"• **{self._fmt_time(ev.timestamp)}** — {ev.description}")
        return {"answer": "\n".join(lines), "sources": ["Evidence DB"]}

    def _overall_confidence(self, db, case_id):
        case = self._get_case(db, case_id)
        if not case:
            return {"answer": "No active investigation.", "sources": []}
        return {
            "answer": (
                f"📊 The overall investigation confidence for **{case.case_name}** is "
                f"**{case.overall_confidence:.1%}** with an evidence rating of "
                f"**{case.evidence_rating}**.\n\n"
                f"- Frames analyzed: {case.total_frames}\n"
                f"- Persons tracked: {case.persons_tracked}\n"
                f"- Suspect matches: {case.matches_found}"
            ),
            "sources": [f"Case: {case.case_name}"],
        }

    def _case_summary(self, db, case_id):
        case = self._get_case(db, case_id)
        if not case:
            return {"answer": "No active investigation found.", "sources": []}
        return {
            "answer": (
                f"📁 **Investigation Summary — {case.case_name}**\n\n"
                f"- Status: **{case.status.upper()}**\n"
                f"- Created: {case.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                f"- Video: {case.video_name or 'N/A'}\n"
                f"- Total frames: {case.total_frames}\n"
                f"- Persons tracked: {case.persons_tracked}\n"
                f"- Matches found: {case.matches_found}\n"
                f"- Overall confidence: {case.overall_confidence:.1%}\n"
                f"- Evidence rating: **{case.evidence_rating}**\n"
                f"- Processing time: {case.processing_time:.1f}s"
            ),
            "sources": [f"Case ID {case.id}"],
        }

    def _clothing_query(self, db, case_id):
        case = self._get_case(db, case_id)
        if not case:
            return {"answer": "No active investigation.", "sources": []}
        ars = (
            db.query(models.AnalysisResult)
            .filter(models.AnalysisResult.case_id == case.id)
            .order_by(models.AnalysisResult.clothing_score.desc())
            .limit(3)
            .all()
        )
        if not ars:
            return {"answer": "No clothing analysis data available.", "sources": []}
        lines = ["👗 **Clothing / Appearance Analysis:**\n"]
        for ar in ars:
            track = db.query(models.Track).filter(models.Track.id == ar.track_id).first()
            tid = track.track_number if track else ar.track_id
            lines.append(
                f"• Track {tid}: clothing match **{ar.clothing_score:.1%}**, "
                f"overall confidence **{ar.final_score:.1%}**"
            )
        return {"answer": "\n".join(lines), "sources": ["Analysis DB", "Clothing scores"]}

    def _fallback(self, db, case_id, question):
        case = self._get_case(db, case_id)
        case_info = f" (Case: {case.case_name})" if case else ""
        return {
            "answer": (
                f"🤖 I couldn't find a specific answer to your query{case_info}. "
                f"Try asking about:\n"
                f"- Track activities (e.g., 'Where did Track 7 appear?')\n"
                f"- Helmet removal events\n"
                f"- Overall confidence scores\n"
                f"- Number of persons detected\n"
                f"- Evidence timeline\n"
                f"- Case investigation summary"
            ),
            "sources": [],
        }

    def _find_track(self, db, case_id, tid):
        case = self._get_case(db, case_id)
        if not case:
            return None
        q = db.query(models.Track).filter(models.Track.case_id == case.id)
        if tid:
            q = q.filter(models.Track.track_number == tid)
        return q.order_by(models.Track.track_number).first()
