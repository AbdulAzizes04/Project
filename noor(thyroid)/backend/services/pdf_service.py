"""
PDF Report Service — ReportLab + QR Code generation
"""
import os, io
from pathlib import Path
from datetime import datetime
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image as RLImage, PageBreak
)
from reportlab.pdfgen import canvas

REPORTS_DIR = Path(__file__).resolve().parent.parent.parent / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

PRIMARY_BLUE = colors.HexColor("#1E40AF")
ACCENT_ORANGE = colors.HexColor("#FB923C")
LIGHT_GRAY = colors.HexColor("#F3F4F6")
MID_GRAY = colors.HexColor("#6B7280")
DANGER_RED = colors.HexColor("#DC2626")
SUCCESS_GREEN = colors.HexColor("#16A34A")
WARNING_YELLOW = colors.HexColor("#D97706")


def _risk_color(risk_level: str):
    return {"High": DANGER_RED, "Medium": WARNING_YELLOW, "Low": SUCCESS_GREEN}.get(risk_level, MID_GRAY)


def _make_qr(data: str) -> io.BytesIO:
    qr = qrcode.QRCode(version=1, box_size=3, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1E40AF", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def generate_report(prediction_data: dict) -> str:
    """Generate a PDF report and return the file path."""
    pid = prediction_data.get("patient_id", "UNKNOWN")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{pid}_{ts}.pdf"
    filepath = str(REPORTS_DIR / filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=15*mm, leftMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', fontSize=18, textColor=PRIMARY_BLUE,
                                 alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=4)
    subtitle_style = ParagraphStyle('Sub', fontSize=10, textColor=MID_GRAY,
                                    alignment=TA_CENTER, fontName='Helvetica', spaceAfter=10)
    heading_style = ParagraphStyle('Heading', fontSize=13, textColor=PRIMARY_BLUE,
                                   fontName='Helvetica-Bold', spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle('Body', fontSize=10, textColor=colors.black,
                                fontName='Helvetica', spaceAfter=4, leading=14)
    bold_style = ParagraphStyle('Bold', fontSize=10, textColor=colors.black,
                                fontName='Helvetica-Bold', spaceAfter=4)

    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    story.append(Paragraph("🏥 ThyroAI Medical Center", title_style))
    story.append(Paragraph("Patient-Specific Thyroid Risk Assessment Report", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY_BLUE, spaceAfter=10))

    # ── Patient Info ──────────────────────────────────────────────────────────
    story.append(Paragraph("Patient Information", heading_style))
    info = prediction_data.get("input_data", {})
    patient_data = [
        ["Patient ID", prediction_data.get("patient_id", "-"),
         "Date", datetime.now().strftime("%d %b %Y %H:%M")],
        ["Name", prediction_data.get("patient_name", "-"),
         "Age / Gender", f"{info.get('age', '-')} / {info.get('gender', '-')}"],
        ["Weight", f"{info.get('weight', '-')} kg",
         "Height", f"{info.get('height', '-')} cm"],
        ["BMI", f"{info.get('bmi', '-')} kg/m²",
         "Blood Pressure", info.get('blood_pressure', '-')],
    ]
    pt = Table(patient_data, colWidths=[38*mm, 55*mm, 38*mm, 55*mm])
    pt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_GRAY),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [LIGHT_GRAY, colors.white]),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(pt)
    story.append(Spacer(1, 6*mm))

    # ── Prediction Result ─────────────────────────────────────────────────────
    story.append(Paragraph("Prediction Result", heading_style))
    condition = prediction_data.get("predicted_condition", "Unknown")
    confidence = prediction_data.get("confidence", 0)
    risk_level = prediction_data.get("risk_level", "Unknown")
    risk_color = _risk_color(risk_level)

    pred_data = [
        ["Predicted Condition", "Confidence", "Risk Level"],
        [condition, f"{confidence:.1f}%", risk_level],
    ]
    pred_table = Table(pred_data, colWidths=[62*mm, 62*mm, 62*mm])
    pred_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWHEIGHTS', (0, 0), (-1, -1), 10*mm),
        ('TEXTCOLOR', (2, 1), (2, 1), risk_color),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, MID_GRAY),
    ]))
    story.append(pred_table)
    story.append(Spacer(1, 6*mm))

    # ── Natural Language Explanation ──────────────────────────────────────────
    story.append(Paragraph("AI Explanation", heading_style))
    nl_exp = prediction_data.get("natural_language_explanation", "")
    story.append(Paragraph(nl_exp, body_style))
    story.append(Spacer(1, 4*mm))

    # ── Top Features ──────────────────────────────────────────────────────────
    story.append(Paragraph("Top Contributing Features (SHAP)", heading_style))
    shap_vals = prediction_data.get("shap_values", {})
    top_feats = sorted(shap_vals.items(), key=lambda x: x[1], reverse=True)[:8]
    if top_feats:
        feat_data = [["Feature", "SHAP Value", "Impact"]]
        for fname, fval in top_feats:
            feat_data.append([fname, f"{fval:.4f}", "↑ Positive" if fval > 0 else "↓ Negative"])
        ft = Table(feat_data, colWidths=[70*mm, 50*mm, 66*mm])
        ft.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), ACCENT_ORANGE),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
            ('GRID', (0, 0), (-1, -1), 0.3, MID_GRAY),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(ft)
    story.append(Spacer(1, 6*mm))

    # ── Model Confidences ─────────────────────────────────────────────────────
    story.append(Paragraph("Ensemble Model Confidences", heading_style))
    mc = prediction_data.get("model_confidences", {})
    mc_data = [
        ["Random Forest", "XGBoost", "LightGBM", "SVM", "ANN"],
        [f"{mc.get('rf', 0):.1f}%", f"{mc.get('xgb', 0):.1f}%",
         f"{mc.get('lgbm', 0):.1f}%", f"{mc.get('svm', 0):.1f}%", f"{mc.get('ann', 0):.1f}%"]
    ]
    mct = Table(mc_data, colWidths=[37*mm]*5)
    mct.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.3, MID_GRAY),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(mct)
    story.append(Spacer(1, 6*mm))

    # ── Doctor Recommendations ────────────────────────────────────────────────
    story.append(Paragraph("Doctor Recommendations", heading_style))
    treatments = prediction_data.get("treatment_suggestions", [])
    lifestyle = prediction_data.get("lifestyle_advice", [])
    diet = prediction_data.get("diet_recommendations", [])
    exercise = prediction_data.get("exercise_recommendations", [])

    for section_title, items in [
        ("Treatment Suggestions", treatments),
        ("Lifestyle Advice", lifestyle),
        ("Diet Recommendations", diet),
        ("Exercise Recommendations", exercise),
    ]:
        if items:
            story.append(Paragraph(f"<b>{section_title}:</b>", bold_style))
            for item in items:
                story.append(Paragraph(f"• {item}", body_style))
            story.append(Spacer(1, 2*mm))

    followup = prediction_data.get("followup_recommendation", "")
    referral = prediction_data.get("referral_suggestion", "")
    if followup:
        story.append(Paragraph(f"<b>Follow-up:</b> {followup}", body_style))
    if referral:
        story.append(Paragraph(f"<b>Referral:</b> {referral}", body_style))

    # ── Doctor Notes ──────────────────────────────────────────────────────────
    notes = prediction_data.get("doctor_notes", "")
    if notes:
        story.append(Paragraph("Doctor Notes", heading_style))
        story.append(Paragraph(notes, body_style))

    # ── QR Code ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 8*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=MID_GRAY, spaceAfter=6))
    qr_buf = _make_qr(f"ThyroAI Report | {pid} | {condition} | {confidence:.1f}%")
    qr_img = RLImage(qr_buf, width=25*mm, height=25*mm)

    footer_data = [
        [qr_img,
         Paragraph(
             f"Generated by ThyroAI Platform | {datetime.now().strftime('%d %b %Y %H:%M')}<br/>"
             f"<font color='#6B7280'>This report is AI-generated and should be reviewed by a qualified medical professional.</font>",
             ParagraphStyle('Footer', fontSize=8, textColor=MID_GRAY, leading=12)
         )]
    ]
    footer_table = Table(footer_data, colWidths=[30*mm, 156*mm])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(footer_table)

    doc.build(story)
    return filename
