"""
VisionTrace AI — DOCX Report Generator (python-docx)
"""
import io
from datetime import datetime
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def _set_cell_bg(cell, hex_color: str):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def _add_heading(doc: Document, text: str, level: int = 1):
    p = doc.add_heading(text, level=level)
    p.runs[0].font.color.rgb = RGBColor(0x00, 0xD4, 0xFF)
    return p


def _add_kv_table(doc: Document, rows: list):
    """Add a 2-column key-value table."""
    table = doc.add_table(rows=len(rows), cols=2)
    table.style = "Table Grid"
    for i, (k, v) in enumerate(rows):
        table.rows[i].cells[0].text = k
        table.rows[i].cells[1].text = str(v)
        _set_cell_bg(table.rows[i].cells[0], "0F1F3D")
        _set_cell_bg(table.rows[i].cells[1], "0A0F1E")
        for cell in table.rows[i].cells:
            for run in cell.paragraphs[0].runs:
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                run.font.size = Pt(10)
    return table


def generate_docx(data: dict) -> bytes:
    case = data["case"]
    tracks = data["tracks"]
    evidence = data["evidence"]
    analysis = data["analysis"]

    doc = Document()

    # ── Page background style (approximated) ──────────────────────────────────
    for section in doc.sections:
        section.page_height = Cm(29.7)
        section.page_width = Cm(21.0)
        section.left_margin = Cm(2)
        section.right_margin = Cm(2)
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)

    # ── Title ─────────────────────────────────────────────────────────────────
    title = doc.add_heading("VISIONTRACE AI", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].font.color.rgb = RGBColor(0x00, 0xD4, 0xFF)
    title.runs[0].font.size = Pt(28)

    sub = doc.add_paragraph("FORENSIC INVESTIGATION REPORT")
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.runs[0].font.bold = True
    sub.runs[0].font.size = Pt(14)
    sub.runs[0].font.color.rgb = RGBColor(0xB0, 0xBE, 0xC5)

    doc.add_paragraph()

    # ── Section 1: Case Info ──────────────────────────────────────────────────
    _add_heading(doc, "1. Case Information")
    _add_kv_table(doc, [
        ("Case ID", case.id),
        ("Case Name", case.case_name),
        ("Date", case.created_at.strftime("%Y-%m-%d %H:%M UTC")),
        ("Status", case.status.upper()),
        ("Video File", case.video_name or "N/A"),
        ("Evidence Rating", case.evidence_rating),
    ])
    doc.add_paragraph()

    # ── Section 2: Investigation Stats ────────────────────────────────────────
    _add_heading(doc, "2. Investigation Statistics")
    _add_kv_table(doc, [
        ("Total Frames Analyzed", case.total_frames),
        ("Persons Tracked", case.persons_tracked),
        ("Suspect Matches Found", case.matches_found),
        ("Overall Confidence", f"{case.overall_confidence:.1%}"),
        ("Processing Time", f"{case.processing_time:.1f} seconds"),
    ])
    doc.add_paragraph()

    # ── Section 3: Tracking Results ───────────────────────────────────────────
    _add_heading(doc, "3. Multi-Target Tracking Results")
    if tracks:
        table = doc.add_table(rows=1 + len(tracks[:20]), cols=6)
        table.style = "Table Grid"
        hdr = ["Track ID", "First Seen", "Last Seen", "Duration", "Detections", "Avg Conf"]
        for i, h in enumerate(hdr):
            c = table.rows[0].cells[i]
            c.text = h
            _set_cell_bg(c, "00D4FF")
            c.paragraphs[0].runs[0].font.bold = True
            c.paragraphs[0].runs[0].font.color.rgb = RGBColor(0x0A, 0x0F, 0x1E)

        def fmt(s): return f"{int(s//60):02d}:{int(s%60):02d}"
        for ri, tr in enumerate(tracks[:20], 1):
            vals = [
                tr.track_number, fmt(tr.first_seen), fmt(tr.last_seen),
                f"{tr.duration:.1f}s", tr.appearance_count, f"{tr.avg_confidence:.1%}",
            ]
            for ci, v in enumerate(vals):
                c = table.rows[ri].cells[ci]
                c.text = str(v)
                _set_cell_bg(c, "0F1F3D" if ri % 2 == 0 else "0A0F1E")
                c.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    doc.add_paragraph()

    # ── Section 4: Analysis Results ───────────────────────────────────────────
    _add_heading(doc, "4. Multi-Modal Analysis Results")
    if analysis:
        table = doc.add_table(rows=1 + len(analysis[:20]), cols=6)
        table.style = "Table Grid"
        hdr = ["Track", "Re-ID", "Gait", "Clothing", "Final Score", "Rating"]
        for i, h in enumerate(hdr):
            c = table.rows[0].cells[i]
            c.text = h
            _set_cell_bg(c, "00D4FF")
            c.paragraphs[0].runs[0].font.bold = True
            c.paragraphs[0].runs[0].font.color.rgb = RGBColor(0x0A, 0x0F, 0x1E)
        for ri, ar in enumerate(analysis[:20], 1):
            vals = [ar.track_id, f"{ar.reid_score:.1%}", f"{ar.gait_score:.1%}",
                    f"{ar.clothing_score:.1%}", f"{ar.final_score:.1%}", ar.evidence_rating]
            for ci, v in enumerate(vals):
                c = table.rows[ri].cells[ci]
                c.text = str(v)
                _set_cell_bg(c, "0F1F3D" if ri % 2 == 0 else "0A0F1E")
                c.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    doc.add_paragraph()

    # ── Section 5: Evidence Timeline ─────────────────────────────────────────
    _add_heading(doc, "5. Evidence Timeline")
    for ev in evidence[:30]:
        def fmt2(s): m, sc = divmod(int(s), 60); return f"{m:02d}:{sc:02d}"
        p = doc.add_paragraph()
        run = p.add_run(f"{fmt2(ev.timestamp)}  —  {ev.description}  [Conf: {ev.confidence:.0%}]")
        run.font.size = Pt(10)
    doc.add_paragraph()

    # ── Section 6: Disclaimer ─────────────────────────────────────────────────
    _add_heading(doc, "6. Disclaimer")
    disc = doc.add_paragraph(
        "This report is generated by VisionTrace AI, an academic prototype system. "
        "All confidence scores are computational estimates derived from AI models. "
        "Results should be reviewed by a qualified forensic professional before "
        "use in any legal or official proceedings. Simulated/demo results are clearly labelled."
    )
    disc.runs[0].font.size = Pt(9)
    disc.runs[0].font.color.rgb = RGBColor(0xFF, 0xC1, 0x07)

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
