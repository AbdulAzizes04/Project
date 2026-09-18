"""
PDF Report Generator for GuidedGuard.

This module generates comprehensive, banking-grade PDF report documents for payment fraud predictions,
incorporating metadata, transaction summary with actual feature values, banking recommendations,
risk score breakdowns, detailed microsecond latency timing, SHAP contribution tables, LIME explanation tables,
embedded SHAP/LIME plots, and structured analyst narrative reports.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

import config


def generate_pdf_report(result_dict: Dict[str, Any], output_path: Optional[Path] = None) -> Path:
    """
    Generate official GuidedGuard Banking Fraud & XAI Audit PDF Report.
    """
    txn_id = str(result_dict.get("transaction_id", "TXN"))
    if output_path is None:
        reports_dir = config.OUTPUTS_DIR / "reports" / "pdf"
        reports_dir.mkdir(parents=True, exist_ok=True)
        output_path = reports_dir / f"GuidedGuard_Audit_Report_{txn_id}.pdf"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY_BLUE = colors.HexColor("#1E3A8A")
    SECONDARY_INDIGO = colors.HexColor("#4F46E5")
    ACCENT_CYAN = colors.HexColor("#0284C7")
    DARK_BG = colors.HexColor("#0F172A")
    LIGHT_BG = colors.HexColor("#F8FAFC")
    TEXT_DARK = colors.HexColor("#1E293B")
    TEXT_MUTED = colors.HexColor("#64748B")

    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.white,
        alignment=TA_LEFT,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#94A3B8"),
        alignment=TA_LEFT,
    )

    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=PRIMARY_BLUE,
        spaceBefore=10,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=TEXT_DARK,
    )

    bold_body_style = ParagraphStyle(
        "BoldBodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=TEXT_DARK,
    )

    narrative_title_style = ParagraphStyle(
        "NarrativeTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=SECONDARY_INDIGO,
    )

    story = []

    # 1. Header Banner Box
    header_data = [
        [
            Paragraph("🛡️ <b>GuidedGuard AI Security</b>", title_style),
            Paragraph(f"<b>Report Date:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/><b>Status:</b> Official Security Audit", ParagraphStyle("HRight", parent=subtitle_style, alignment=TA_RIGHT, textColor=colors.white))
        ],
        [
            Paragraph("Explainable Digital Payment Scam Detection & Risk Governance Report", subtitle_style),
            Paragraph(f"<b>Transaction ID:</b> {txn_id}", ParagraphStyle("HRight2", parent=subtitle_style, alignment=TA_RIGHT, textColor=colors.HexColor("#CBD5E1")))
        ]
    ]

    header_table = Table(header_data, colWidths=[340, 200])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), PRIMARY_BLUE),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))

    # 2. Executive Prediction & Banking Recommendation Banner
    pred_label = result_dict.get("prediction", "Legitimate")
    risk_score = result_dict.get("risk_score", 0)
    risk_level = result_dict.get("risk_level", "LOW")
    scam_prob = result_dict.get("scam_probability", 0.0)
    rec_obj = result_dict.get("banking_recommendation", {})
    action_str = rec_obj.get("action", "Approve")
    rec_text = rec_obj.get("recommendation", "Approve Transaction")
    rec_details = rec_obj.get("details", "")

    banner_bg = colors.HexColor("#DC2626") if pred_label.lower() in ["scam", "fraudulent", "scam / fraudulent"] else colors.HexColor("#16A34A")

    rec_box_data = [
        [
            Paragraph(f"<font color='white' size=12><b>PREDICTION: {pred_label.upper()}</b></font>", ParagraphStyle("PBox", parent=title_style)),
            Paragraph(f"<font color='white' size=12><b>RISK SCORE: {risk_score} / 100 ({risk_level} RISK)</b></font>", ParagraphStyle("PBoxR", parent=title_style, alignment=TA_RIGHT))
        ],
        [
            Paragraph(f"<font color='white'><b>Scam Probability:</b> {scam_prob*100:.2f}% &nbsp;|&nbsp; <b>Model Confidence:</b> {result_dict.get('confidence_pct', 99.0):.2f}%</font>", subtitle_style),
            Paragraph(f"<font color='white'><b>Banking Action:</b> {action_str.upper()}</font>", ParagraphStyle("PBoxR2", parent=subtitle_style, alignment=TA_RIGHT))
        ],
        [
            Paragraph(f"<font color='white'><b>Official Recommendation:</b> {rec_text}. {rec_details}</font>", ParagraphStyle("RecDetail", parent=subtitle_style, leading=12)),
            Paragraph("", subtitle_style)
        ]
    ]

    rec_table = Table(rec_box_data, colWidths=[340, 200])
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), banner_bg),
        ('SPAN', (0, 2), (1, 2)),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 12))

    # 3. Transaction Summary & Actual Feature Values Table
    story.append(Paragraph("1. Transaction Details & Actual Parameter Values", h1_style))

    raw_payload = result_dict.get("raw_payload", {})
    feature_values = result_dict.get("actual_feature_values", {})

    txn_grid = [
        [
            Paragraph("<b>Transaction ID:</b>", body_style), Paragraph(str(result_dict.get("transaction_id")), body_style),
            Paragraph("<b>Transaction Amount:</b>", body_style), Paragraph(str(feature_values.get("amount", raw_payload.get("amount"))), bold_body_style),
        ],
        [
            Paragraph("<b>Customer ID:</b>", body_style), Paragraph(str(raw_payload.get("customer_id", "C123456789")), body_style),
            Paragraph("<b>Sender Old Balance:</b>", body_style), Paragraph(str(feature_values.get("old_balance_orig", raw_payload.get("old_balance_orig"))), body_style),
        ],
        [
            Paragraph("<b>Beneficiary ID:</b>", body_style), Paragraph(str(raw_payload.get("beneficiary_id", "M987654321")), body_style),
            Paragraph("<b>Sender New Balance:</b>", body_style), Paragraph(str(feature_values.get("new_balance_orig", raw_payload.get("new_balance_orig"))), body_style),
        ],
        [
            Paragraph("<b>Payment Type:</b>", body_style), Paragraph(str(raw_payload.get("transaction_type", raw_payload.get("type", "TRANSFER"))), body_style),
            Paragraph("<b>Receiver Old Balance:</b>", body_style), Paragraph(str(feature_values.get("old_balance_dest", raw_payload.get("old_balance_dest"))), body_style),
        ],
        [
            Paragraph("<b>Device Type:</b>", body_style), Paragraph(str(feature_values.get("device_type", raw_payload.get("device_type"))), body_style),
            Paragraph("<b>Receiver New Balance:</b>", body_style), Paragraph(str(feature_values.get("new_balance_dest", raw_payload.get("new_balance_dest"))), body_style),
        ],
        [
            Paragraph("<b>Location Region:</b>", body_style), Paragraph(str(feature_values.get("location", raw_payload.get("location"))), body_style),
            Paragraph("<b>6h Transaction Velocity:</b>", body_style), Paragraph(str(feature_values.get("velocity_6h", raw_payload.get("velocity_6h"))), body_style),
        ],
        [
            Paragraph("<b>New Beneficiary:</b>", body_style), Paragraph(str(feature_values.get("is_new_beneficiary", "No")), body_style),
            Paragraph("<b>Prior Fraud History:</b>", body_style), Paragraph(str(feature_values.get("beneficiary_fraud_history_flag", "No")), body_style),
        ],
    ]

    t_grid = Table(txn_grid, colWidths=[130, 140, 130, 140])
    t_grid.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_grid)
    story.append(Spacer(1, 12))

    # 4. Risk Score Breakdown Panel & Latency Timing Table
    story.append(Paragraph("2. Composite Risk Score Breakdown & Latency Timing", h1_style))

    risk_bd = result_dict.get("risk_score_breakdown", {})
    timing_bd = result_dict.get("latency_breakdown", {})

    risk_table_data = [
        [Paragraph("<b>Risk Dimension</b>", bold_body_style), Paragraph("<b>Sub-Score</b>", bold_body_style), Paragraph("<b>Status & Impact</b>", bold_body_style)],
        [Paragraph("Model Fraud Probability", body_style), Paragraph(f"{risk_bd.get('model_probability', 0):.2f}%", body_style), Paragraph(f"Weight: 70% (Score: {risk_bd.get('model_probability_score', 0):.1f})", body_style)],
        [Paragraph("Amount Risk", body_style), Paragraph(f"{risk_bd.get('amount_risk', 0):.1f} pts", body_style), Paragraph("Transaction size evaluation", body_style)],
        [Paragraph("Velocity Risk", body_style), Paragraph(f"{risk_bd.get('velocity_risk', 0):.1f} pts", body_style), Paragraph("6-hour transaction frequency", body_style)],
        [Paragraph("Device Risk", body_style), Paragraph(f"{risk_bd.get('device_risk', 0):.1f} pts", body_style), Paragraph("Device profile verification", body_style)],
        [Paragraph("Location Risk", body_style), Paragraph(f"{risk_bd.get('location_risk', 0):.1f} pts", body_style), Paragraph("Geographic regional risk", body_style)],
        [Paragraph("Beneficiary Risk", body_style), Paragraph(f"{risk_bd.get('beneficiary_risk', 0):.1f} pts", body_style), Paragraph("New beneficiary check", body_style)],
        [Paragraph("Historical Behaviour", body_style), Paragraph(f"{risk_bd.get('historical_behaviour', 0):.1f} pts", body_style), Paragraph("Prior fraud flag check", body_style)],
        [Paragraph("Balance Behaviour", body_style), Paragraph(f"{risk_bd.get('balance_behaviour', 0):.1f} pts", body_style), Paragraph("Account wipeout detection", body_style)],
        [Paragraph("<b>FINAL COMPOSITE RISK SCORE</b>", bold_body_style), Paragraph(f"<b>{risk_bd.get('final_risk_score', risk_score)} / 100</b>", bold_body_style), Paragraph(f"<b>{risk_level} RISK CATEGORY</b>", bold_body_style)],
    ]

    t_risk = Table(risk_table_data, colWidths=[180, 120, 240])
    t_risk.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EEF2FF")),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#E0E7FF")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_risk)
    story.append(Spacer(1, 8))

    # Latency Timing Row
    timing_data = [
        [
            Paragraph(f"<b>Feature Eng:</b> {timing_bd.get('feature_engineering', 0):.2f} ms", body_style),
            Paragraph(f"<b>Prediction:</b> {timing_bd.get('prediction', 0):.2f} ms", body_style),
            Paragraph(f"<b>SHAP Engine:</b> {timing_bd.get('shap', 0):.2f} ms", body_style),
            Paragraph(f"<b>LIME Engine:</b> {timing_bd.get('lime', 0):.2f} ms", body_style),
            Paragraph(f"<b>Rendering:</b> {timing_bd.get('rendering', 0):.2f} ms", body_style),
            Paragraph(f"<b>TOTAL:</b> {timing_bd.get('total', result_dict.get('latency_ms', 0)):.2f} ms", bold_body_style),
        ]
    ]
    t_timing = Table(timing_data, colWidths=[90, 90, 90, 90, 90, 90])
    t_timing.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_timing)
    story.append(Spacer(1, 12))

    # 5. Banking Analyst Narrative Report
    story.append(Paragraph("3. Banking-Grade Analyst Narrative Report", h1_style))
    analyst_rpt = result_dict.get("analyst_report", {})

    narrative_rows = [
        [Paragraph("<b>Transaction Summary:</b>", narrative_title_style), Paragraph(analyst_rpt.get("transaction_summary", ""), body_style)],
        [Paragraph("<b>Behaviour Analysis:</b>", narrative_title_style), Paragraph(analyst_rpt.get("behaviour_analysis", ""), body_style)],
        [Paragraph("<b>High Risk Indicators:</b>", narrative_title_style), Paragraph("; ".join(analyst_rpt.get("high_risk_indicators", ["None"])) if analyst_rpt.get("high_risk_indicators") else "None identified.", body_style)],
        [Paragraph("<b>Safe Indicators:</b>", narrative_title_style), Paragraph("; ".join(analyst_rpt.get("safe_indicators", ["None"])) if analyst_rpt.get("safe_indicators") else "None identified.", body_style)],
        [Paragraph("<b>Model Explanation:</b>", narrative_title_style), Paragraph(analyst_rpt.get("model_explanation", ""), body_style)],
        [Paragraph("<b>SHAP Summary:</b>", narrative_title_style), Paragraph(analyst_rpt.get("shap_summary", ""), body_style)],
        [Paragraph("<b>Final Recommendation:</b>", narrative_title_style), Paragraph(analyst_rpt.get("final_recommendation", ""), bold_body_style)],
    ]

    t_narrative = Table(narrative_rows, colWidths=[130, 410])
    t_narrative.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_narrative)
    story.append(Spacer(1, 14))

    # 6. Top 10 SHAP Contribution Table & Image
    story.append(Paragraph("4. Top 10 SHAP Feature Contribution Attributions", h1_style))

    shap_factors = result_dict.get("top_risk_factors", [])
    shap_table_data = [
        [
            Paragraph("<b>Feature Name</b>", bold_body_style),
            Paragraph("<b>Actual Value</b>", bold_body_style),
            Paragraph("<b>SHAP Value</b>", bold_body_style),
            Paragraph("<b>Contrib %</b>", bold_body_style),
            Paragraph("<b>Direction</b>", bold_body_style),
            Paragraph("<b>Impact Level</b>", bold_body_style),
        ]
    ]

    for f in shap_factors[:10]:
        shap_table_data.append([
            Paragraph(str(f.get("feature_name", f.get("feature"))), body_style),
            Paragraph(str(f.get("actual_value", "0")), body_style),
            Paragraph(f"{f.get('shap_value', f.get('impact', 0)):+.4f}", body_style),
            Paragraph(f"{f.get('contribution_pct', 0):.2f}%", body_style),
            Paragraph(str(f.get("direction_label", f.get("direction"))), body_style),
            Paragraph(str(f.get("impact_level", "Medium")), body_style),
        ])

    t_shap = Table(shap_table_data, colWidths=[130, 90, 80, 70, 95, 75])
    t_shap.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EFF6FF")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_shap)
    story.append(Spacer(1, 10))

    # SHAP Waterfall Image
    shap_plots = result_dict.get("shap_plots", {})
    waterfall_path = shap_plots.get("waterfall_plot_png")
    if waterfall_path and Path(waterfall_path).exists():
        try:
            img_shap = Image(str(waterfall_path), width=520, height=240)
            story.append(img_shap)
            story.append(Spacer(1, 14))
        except Exception:
            pass

    # 7. LIME Decision Rules Table & Image
    story.append(Paragraph("5. Local LIME Decision Rules & Explanations", h1_style))

    lime_table_data_raw = result_dict.get("lime_table", [])
    lime_table_data = [
        [
            Paragraph("<b>Decision Rule Condition</b>", bold_body_style),
            Paragraph("<b>Rule Weight</b>", bold_body_style),
            Paragraph("<b>Effect Direction</b>", bold_body_style),
            Paragraph("<b>Domain Explanation</b>", bold_body_style),
        ]
    ]

    for item in lime_table_data_raw[:10]:
        lime_table_data.append([
            Paragraph(str(item.get("decision_rule")), body_style),
            Paragraph(f"{item.get('rule_weight', 0):+.4f}", body_style),
            Paragraph(str(item.get("effect_label", item.get("effect"))), body_style),
            Paragraph(str(item.get("explanation")), body_style),
        ])

    t_lime = Table(lime_table_data, colWidths=[150, 75, 95, 220])
    t_lime.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#FEF3C7")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_lime)
    story.append(Spacer(1, 10))

    # LIME Rules Plot Image
    lime_plots = result_dict.get("lime_plots", {})
    lime_img_path = lime_plots.get("lime_plot_png")
    if lime_img_path and Path(lime_img_path).exists():
        try:
            img_lime = Image(str(lime_img_path), width=520, height=240)
            story.append(img_lime)
        except Exception:
            pass

    # Build Document
    doc.build(story)
    return output_path
