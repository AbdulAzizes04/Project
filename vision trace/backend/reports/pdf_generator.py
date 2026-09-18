"""
VisionTrace AI — PDF Report Generator (ReportLab)
"""
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak,
)


# ── Colour palette ────────────────────────────────────────────────────────────
DARK_BG = colors.HexColor("#0a0f1e")
NAVY = colors.HexColor("#0f1f3d")
CYAN = colors.HexColor("#00d4ff")
GREEN = colors.HexColor("#00ff88")
YELLOW = colors.HexColor("#ffc107")
RED = colors.HexColor("#ff4444")
WHITE = colors.white
LIGHT_GREY = colors.HexColor("#b0bec5")


def _rating_color(rating: str):
    return {"HIGH": GREEN, "MEDIUM": YELLOW, "LOW": RED}.get(rating, LIGHT_GREY)


def generate_pdf(data: dict) -> bytes:
    case = data["case"]
    tracks = data["tracks"]
    evidence = data["evidence"]
    analysis = data["analysis"]

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=20 * mm, bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()

    def style(name, **kw):
        return ParagraphStyle(name, **{
            "fontName": "Helvetica", "textColor": WHITE, **kw,
        })

    title_style = style("Title", fontSize=22, leading=28, spaceAfter=4)
    subtitle_style = style("Sub", fontSize=11, textColor=CYAN, spaceAfter=12)
    h2_style = style("H2", fontSize=14, leading=18, spaceBefore=12, spaceAfter=6, textColor=CYAN)
    body_style = style("Body", fontSize=10, leading=14, textColor=LIGHT_GREY)
    label_style = style("Label", fontSize=9, textColor=CYAN)

    story = []

    # ── Cover ──────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph("VISIONTRACE AI", title_style))
    story.append(Paragraph("FORENSIC INVESTIGATION REPORT", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN))
    story.append(Spacer(1, 0.5 * cm))

    cover_data = [
        ["Case ID", str(case.id)],
        ["Case Name", case.case_name],
        ["Date", case.created_at.strftime("%Y-%m-%d %H:%M UTC")],
        ["Status", case.status.upper()],
        ["Evidence Rating", case.evidence_rating],
    ]
    t = Table(cover_data, colWidths=[50 * mm, 100 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, -1), WHITE),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [NAVY, DARK_BG]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#1a2a4a")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(PageBreak())

    # ── Section 1: Case Information ────────────────────────────────────────────
    story.append(Paragraph("1. Case Information", h2_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=CYAN))
    story.append(Spacer(1, 3 * mm))

    info_data = [
        ["Video File", case.video_name or "N/A"],
        ["Total Frames Analyzed", str(case.total_frames)],
        ["Persons Tracked", str(case.persons_tracked)],
        ["Suspect Matches", str(case.matches_found)],
        ["Overall Confidence", f"{case.overall_confidence:.1%}"],
        ["Processing Time", f"{case.processing_time:.1f}s"],
        ["Evidence Rating", case.evidence_rating],
    ]
    t2 = Table(info_data, colWidths=[60 * mm, 100 * mm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, -1), WHITE),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [NAVY, DARK_BG]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#1a2a4a")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t2)
    story.append(Spacer(1, 6 * mm))

    # ── Section 2: Tracking Results ────────────────────────────────────────────
    story.append(Paragraph("2. Multi-Target Tracking Results", h2_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=CYAN))
    story.append(Spacer(1, 3 * mm))

    if tracks:
        headers = ["Track ID", "First Seen", "Last Seen", "Duration", "Detections", "Avg Conf"]
        track_rows = [headers]
        for tr in tracks[:20]:
            def fmt(s): return f"{int(s//60):02d}:{int(s%60):02d}"
            track_rows.append([
                str(tr.track_number), fmt(tr.first_seen), fmt(tr.last_seen),
                f"{tr.duration:.1f}s", str(tr.appearance_count), f"{tr.avg_confidence:.1%}",
            ])
        t3 = Table(track_rows, colWidths=[25 * mm] * 6)
        t3.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), CYAN),
            ("TEXTCOLOR", (0, 0), (-1, 0), DARK_BG),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (0, 1), (-1, -1), WHITE),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [DARK_BG, NAVY]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#1a2a4a")),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t3)
    else:
        story.append(Paragraph("No track data available.", body_style))
    story.append(Spacer(1, 6 * mm))

    # ── Section 3: Analysis Results ────────────────────────────────────────────
    story.append(Paragraph("3. Multi-Modal Analysis Results", h2_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=CYAN))
    story.append(Spacer(1, 3 * mm))

    if analysis:
        headers = ["Track", "Re-ID", "Gait", "Clothing", "Final Score", "Rating"]
        ar_rows = [headers]
        for ar in analysis[:20]:
            ar_rows.append([
                str(ar.track_id), f"{ar.reid_score:.1%}", f"{ar.gait_score:.1%}",
                f"{ar.clothing_score:.1%}", f"{ar.final_score:.1%}", ar.evidence_rating,
            ])
        t4 = Table(ar_rows, colWidths=[25 * mm, 25 * mm, 25 * mm, 25 * mm, 30 * mm, 25 * mm])
        t4.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), CYAN),
            ("TEXTCOLOR", (0, 0), (-1, 0), DARK_BG),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (0, 1), (-1, -1), WHITE),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [DARK_BG, NAVY]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#1a2a4a")),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t4)
    story.append(Spacer(1, 6 * mm))

    # ── Section 4: Evidence Timeline ──────────────────────────────────────────
    story.append(Paragraph("4. Evidence Timeline", h2_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=CYAN))
    story.append(Spacer(1, 3 * mm))

    for ev in evidence[:30]:
        def fmt2(s): m, sc = divmod(int(s), 60); return f"{m:02d}:{sc:02d}"
        story.append(Paragraph(
            f"<b>{fmt2(ev.timestamp)}</b>  —  {ev.description}  "
            f"[Conf: {ev.confidence:.0%}]",
            body_style,
        ))
        story.append(Spacer(1, 2 * mm))

    # ── Section 5: Summary ─────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("5. AI Investigation Summary", h2_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=CYAN))
    story.append(Spacer(1, 3 * mm))

    rating_col = _rating_color(case.evidence_rating)
    summary_text = (
        f"The VisionTrace AI system analyzed the uploaded CCTV surveillance footage "
        f"({case.video_name or 'N/A'}) and detected {case.persons_tracked} unique individuals "
        f"across {case.total_frames} processed frames. "
        f"Multi-modal forensic analysis combining Person Re-Identification, Gait Analysis, "
        f"and Appearance Comparison yielded an overall confidence of "
        f"{case.overall_confidence:.1%} with an evidence rating of {case.evidence_rating}. "
        f"A total of {case.matches_found} candidate matches exceeded the configured similarity threshold. "
        f"This report is generated by an AI prototype system and is intended for "
        f"academic and investigative assistance purposes only. Results are NOT legally conclusive."
    )
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        f"⚠️  DISCLAIMER: This is an AI-generated forensic analysis prototype. "
        f"All confidence scores are computational estimates and should be reviewed "
        f"by a qualified forensic professional before use in legal proceedings.",
        ParagraphStyle("Disclaimer", fontName="Helvetica-Oblique", fontSize=9,
                       textColor=YELLOW, leading=13),
    ))

    doc.build(story, onFirstPage=_page_header, onLaterPages=_page_header)
    return buf.getvalue()


def _page_header(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#0a0f1e"))
    canvas.rect(0, 0, A4[0], A4[1], fill=1)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(colors.HexColor("#00d4ff"))
    canvas.drawString(20 * mm, A4[1] - 12 * mm, "VISIONTRACE AI — FORENSIC INVESTIGATION REPORT")
    canvas.drawRightString(A4[0] - 20 * mm, A4[1] - 12 * mm,
                           f"Page {doc.page} | {datetime.now().strftime('%Y-%m-%d')}")
    canvas.restoreState()
