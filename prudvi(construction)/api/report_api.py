"""
ReportLab PDF Report Generator for BuildVerse AI.
Generates executive PDF reports with header, metrics, tables, images, and AI recommendations.
"""

import os
from pathlib import Path
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from config import UPLOADS_REPORTS

def generate_pdf_report(project: Dict[str, Any], progress_log: Dict[str, Any] = None) -> str:
    """Generates a PDF construction report and returns file path."""
    p_id = project.get("id", 1)
    p_name = project.get("name", "Project")
    
    file_path = UPLOADS_REPORTS / f"BuildVerse_Report_Project_{p_id}.pdf"
    doc = SimpleDocTemplate(str(file_path), pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=colors.HexColor('#0891B2'),
        spaceAfter=10
    )
    
    subtitle_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=15
    )
    
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=8
    )

    h2_style = ParagraphStyle(
        'Heading2Dark',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#0891B2'),
        spaceBefore=12,
        spaceAfter=6
    )

    story = []
    
    # 1. Header Banner
    story.append(Paragraph("BuildVerse AI — Construction Executive Report", title_style))
    story.append(Paragraph(f"Project Name: <b>{p_name}</b> | Owner: <b>{project.get('owner_name', 'Owner')}</b> | Location: <b>{project.get('location', 'Site')}</b>", subtitle_style))
    story.append(Spacer(1, 10))
    
    # 2. Key Metrics Summary Table
    overall_pct = progress_log.get("overall_progress_pct", 0.0) if progress_log else 0.0
    status_str = progress_log.get("status", "On Schedule") if progress_log else "On Schedule"
    
    metrics_data = [
        ["Plot Area", f"{project.get('plot_area', 0)} {project.get('plot_unit', 'sq.ft')}", "Total Budget", f"${project.get('budget', 0):,.2f}"],
        ["Floors", f"{project.get('num_floors', 1)} Floor(s)", "Workers On-Site", f"{project.get('workers_available', 10)}"],
        ["Overall Construction %", f"{overall_pct:.1f}%", "Current Status", status_str],
        ["Start Date", f"{project.get('start_date', 'N/A')}", "Target Completion", f"{project.get('completion_date', 'N/A')}"]
    ]
    
    t = Table(metrics_data, colWidths=[130, 130, 130, 130])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#0F172A')),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BAE6FD')),
        ('BACKGROUND', (0,2), (1,2), colors.HexColor('#E0F2FE')),
        ('TEXTCOLOR', (0,2), (1,2), colors.HexColor('#0891B2')),
        ('FONTNAME', (0,2), (1,2), 'Helvetica-Bold')
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    # 3. AI Site Findings & Recommendations
    story.append(Paragraph("AI Site Progress & Quality Evaluation", h2_style))
    if progress_log:
        summary_text = progress_log.get("ai_summary", "Site inspection completed cleanly.")
        rec_text = progress_log.get("ai_recommendation", "Continue scheduled operations.")
    else:
        summary_text = "Standard milestone schedule generated. No active site delays reported."
        rec_text = "Maintain planned worker velocity and material staging."
        
    story.append(Paragraph(f"<b>Summary:</b> {summary_text}", body_style))
    story.append(Paragraph(f"<b>AI Recommendation:</b> {rec_text}", body_style))
    story.append(Spacer(1, 15))

    # 4. Construction Phase Timeline Table
    story.append(Paragraph("Construction Phase Timeline Breakdown", h2_style))
    schedules = project.get("schedules", [])
    
    if schedules:
        phase_table_data = [["Phase Name", "Start Date", "End Date", "Duration", "Budget Cost", "Status"]]
        for s in schedules[:12]:
            phase_table_data.append([
                s.get("phase_name", ""),
                s.get("start_date", ""),
                s.get("end_date", ""),
                f"{s.get('duration_days', 0)} d",
                f"${s.get('cost', 0):,.0f}",
                s.get("status", "Pending")
            ])
            
        t_phase = Table(phase_table_data, colWidths=[110, 80, 80, 60, 90, 100])
        t_phase.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0891B2')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
        ]))
        story.append(t_phase)
        
    story.append(Spacer(1, 20))
    story.append(Paragraph("BuildVerse AI — Automated Digital Twin Platform Report", ParagraphStyle('Footer', parent=styles['Italic'], fontSize=8, textColor=colors.HexColor('#64748B'))))

    doc.build(story)
    return str(file_path)
