"""
Sleep Disorder AI - Clinical PDF Report Generator
Uses ReportLab to build an executive, publication-grade clinical assessment report.
"""
import os
import io
import json
import base64
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, KeepTogether
)
from reportlab.lib.units import inch

class ReportService:
    @staticmethod
    def generate_assessment_pdf(assessment, user, output_path=None):
        """
        Builds a comprehensive, professionally styled PDF report.
        Args:
            assessment: Assessment ORM object
            user: User ORM object
            output_path: optional filepath. If None, returns BytesIO buffer.
        """
        buffer = io.BytesIO() if output_path is None else output_path
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
        )
        
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#1e3a8a"),
            fontName="Helvetica-Bold",
            alignment=1
        )
        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#475569"),
            alignment=1
        )
        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#1e3a8a"),
            fontName="Helvetica-Bold",
            spaceBefore=10,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#1e293b")
        )
        disclaimer_style = ParagraphStyle(
            "Disclaimer",
            parent=styles["Normal"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#b91c1c"),
            fontName="Helvetica-Oblique",
            alignment=1
        )
        
        elements = []
        
        # Header / Hospital banner
        elements.append(Paragraph("SLEEPAI CLINICAL DECISION SUPPORT", title_style))
        elements.append(Paragraph("An Explainable AI Framework for Intelligent Sleep Disorder Screening", subtitle_style))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1e3a8a"), spaceAfter=12))
        
        # Patient & Assessment Meta Table
        input_data = json.loads(assessment.input_data) if isinstance(assessment.input_data, str) else assessment.input_data
        
        meta_data = [
            [
                Paragraph("<b>Patient Name:</b> " + str(user.name), body_style),
                Paragraph("<b>Assessment ID:</b> #" + str(assessment.id), body_style)
            ],
            [
                Paragraph("<b>Email:</b> " + str(user.email), body_style),
                Paragraph("<b>Date:</b> " + assessment.assessment_date.strftime("%B %d, %Y %H:%M UTC"), body_style)
            ],
            [
                Paragraph("<b>Model Architecture:</b> " + str(assessment.model_name), body_style),
                Paragraph("<b>Classification Mode:</b> Multi-Class Screening", body_style)
            ]
        ]
        meta_table = Table(meta_data, colWidths=[260, 260])
        meta_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 14))
        
        # Primary Finding Box
        pred_class = assessment.predicted_class
        conf = round(assessment.confidence, 1)
        bg_color = "#dcfce7" if pred_class == "None" else ("#fef9c3" if pred_class == "Insomnia" else "#fee2e2")
        border_color = "#16a34a" if pred_class == "None" else ("#ca8a04" if pred_class == "Insomnia" else "#dc2626")
        
        finding_html = f"""
        <b>Preliminary Screening Result:</b> <font size="14" color="{border_color}"><b>{pred_class}</b></font> 
        &nbsp;&nbsp;|&nbsp;&nbsp; <b>Model Confidence:</b> <b>{conf}%</b>
        """
        finding_data = [[Paragraph(finding_html, body_style)]]
        finding_table = Table(finding_data, colWidths=[520])
        finding_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg_color)),
            ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor(border_color)),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 14),
            ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ]))
        elements.append(finding_table)
        elements.append(Spacer(1, 14))
        
        # Section: Patient Input Parameters
        elements.append(Paragraph("Clinical & Lifestyle Parameters Recorded", section_heading))
        params_data = [
            ["Age", str(input_data.get("Age")), "Sleep Duration", f"{input_data.get('Sleep Duration')} hrs"],
            ["Gender", str(input_data.get("Gender")), "Quality of Sleep", f"{input_data.get('Quality of Sleep')}/10"],
            ["Occupation", str(input_data.get("Occupation")), "Stress Level", f"{input_data.get('Stress Level')}/10"],
            ["BMI Category", str(input_data.get("BMI Category")), "Physical Activity", f"{input_data.get('Physical Activity Level')} min/day"],
            ["Blood Pressure", f"{input_data.get('Systolic_BP')}/{input_data.get('Diastolic_BP')} mmHg", "Daily Steps", str(input_data.get("Daily Steps"))],
            ["Resting Heart Rate", f"{input_data.get('Heart Rate')} bpm", "", ""]
        ]
        params_table = Table(params_data, colWidths=[130, 130, 130, 130])
        params_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
            ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#f1f5f9")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0f172a")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(params_table)
        elements.append(Spacer(1, 14))
        
        # Section: Multiclass Probabilities
        elements.append(Paragraph("Multi-Class Prediction Probability Distribution", section_heading))
        prob_headers = ["Classification Category", "Probability", "Risk Indication"]
        prob_rows = [prob_headers]
        for p in assessment.predictions:
            risk_desc = "Optimal Baseline" if p.class_name == "None" else ("Sleep Disturbance Risk" if p.class_name == "Insomnia" else "Respiratory Obstruction Risk")
            prob_rows.append([p.class_name, f"{p.probability:.2f}%", risk_desc])
            
        prob_table = Table(prob_rows, colWidths=[180, 140, 200])
        prob_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(prob_table)
        elements.append(Spacer(1, 14))
        
        # Section: SHAP Explainable AI
        elements.append(Paragraph("Explainable AI (XAI) - SHAP Feature Attribution", section_heading))
        shap_intro = (
            "SHAP (SHapley Additive exPlanations) attributes log-odds contribution values to each patient feature, "
            "revealing the transparent causal drivers behind this model's decision."
        )
        elements.append(Paragraph(shap_intro, body_style))
        elements.append(Spacer(1, 6))
        
        shap_headers = ["Top Contributing Clinical Factor", "SHAP Impact", "Effect on Screening"]
        shap_rows = [shap_headers]
        for exp in assessment.explanations:
            effect_text = "Elevates Risk" if exp.contribution_type == "Positive" else "Protective Factor"
            shap_rows.append([exp.feature_name, f"{exp.shap_value:+.4f}", effect_text])
            
        shap_table = Table(shap_rows, colWidths=[240, 120, 160])
        shap_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(shap_table)
        elements.append(Spacer(1, 14))
        
        # Section: Preventive Health Recommendations (Gemini AI)
        elements.append(Paragraph("Personalized Sleep & Lifestyle Recommendations (Powered by Gemini AI)", section_heading))
        rec_text = "No recommendations recorded."
        if assessment.recommendations:
            rec_text = assessment.recommendations[0].recommendation_text
            
        # Parse recommendation lines cleanly into separate paragraphs
        lines = rec_text.split("\n")
        for line in lines:
            line_str = line.strip()
            if not line_str:
                elements.append(Spacer(1, 4))
                continue
            if line_str.startswith("### "):
                title = line_str.replace("### ", "").strip()
                elements.append(Paragraph(f"<b>{title}</b>", ParagraphStyle("SubHead", parent=body_style, fontName="Helvetica-Bold", textColor=colors.HexColor("#1e3a8a"), spaceBefore=6)))
            elif line_str.startswith("- ") or line_str.startswith("* "):
                bullet_content = line_str[2:].replace("**", "<b>", 1).replace("**", "</b>", 1)
                elements.append(Paragraph(f"&bull; {bullet_content}", body_style))
            else:
                cleaned_line = line_str.replace("**", "<b>", 1).replace("**", "</b>", 1)
                elements.append(Paragraph(cleaned_line, body_style))
                
        elements.append(Spacer(1, 15))
        
        # Footer Medical Disclaimer
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=8))
        disclaimer_text = (
            "IMPORTANT CLINICAL NOTICE: This system is intended for educational and preliminary screening purposes only "
            "and does not constitute a medical diagnosis. Predictions are generated using machine learning models trained "
            "on clinical research datasets. Users experiencing chronic fatigue, persistent insomnia, or breathing pauses "
            "during sleep should consult a qualified healthcare professional or board-certified sleep specialist."
        )
        elements.append(Paragraph(disclaimer_text, disclaimer_style))
        
        # Build Document
        doc.build(elements)
        
        if output_path is None:
            buffer.seek(0)
            return buffer.getvalue()
        return output_path
