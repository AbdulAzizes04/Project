import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "BuildVerse AI — Comprehensive System Documentation")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)

        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 40, page_text)
        self.drawString(54, 40, "Confidential & Proprietary • BuildVerse AI Engineering")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 52, 558, 52)
        self.restoreState()

def generate_pdf(output_path):
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=64,
        bottomMargin=64
    )

    primary_cyan = colors.HexColor("#0891B2")
    secondary_cyan = colors.HexColor("#06B6D4")
    dark_slate = colors.HexColor("#0F172A")
    light_cyan_bg = colors.HexColor("#F0F9FF")
    border_cyan = colors.HexColor("#BAE6FD")
    text_muted = colors.HexColor("#475569")
    table_header_bg = colors.HexColor("#0891B2")
    row_alt_bg = colors.HexColor("#F8FAFC")

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_cyan,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=text_muted,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=primary_cyan,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=dark_slate,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=dark_slate,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    table_hdr_style = ParagraphStyle(
        'TableHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=dark_slate
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=primary_cyan
    )

    banner_style = ParagraphStyle(
        'BannerText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=dark_slate
    )

    story = []

    # Title Banner
    story.append(Spacer(1, 10))
    story.append(Paragraph("🏗️ BuildVerse AI", title_style))
    story.append(Paragraph("Comprehensive Project Architecture, Technical Specifications & Operational Blueprint", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=primary_cyan, spaceAfter=14))

    # Meta Info Card Table
    meta_data = [
        [
            Paragraph("<b>Platform:</b> BuildVerse AI (Digital Twin & Site Monitoring)", table_cell_style),
            Paragraph("<b>Version:</b> 1.0.0 (Production Architecture)", table_cell_style)
        ],
        [
            Paragraph("<b>Runtime:</b> Python 3.11 • Streamlit • Plotly", table_cell_style),
            Paragraph("<b>Target Domain:</b> Civil Engineering & Smart Construction", table_cell_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[250, 254])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), light_cyan_bg),
        ('BOX', (0, 0), (-1, -1), 1, border_cyan),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # Section 1: Why It Is Important
    story.append(Paragraph("1. Executive Summary & Problem Context", h1_style))
    story.append(Paragraph(
        "Construction is historically one of the world's least digitized mega-industries. "
        "According to global infrastructure benchmarks, over <b>70% of construction projects</b> experience significant timeline delays, "
        "budget overruns, and rework costs. BuildVerse AI was conceived to eliminate these core vulnerabilities through automated intelligence.",
        body_style
    ))
    
    story.append(Paragraph("<b>Primary Industry Challenges Addressed:</b>", body_style))
    story.append(Paragraph("• <b>Subjective & Inefficient Site Inspections:</b> Manual inspection methods rely on sporadic physical site walkthroughs. Reports are delivered days later, making root-cause interventions obsolete.", bullet_style))
    story.append(Paragraph("• <b>The Disconnect Between Blueprint and Reality:</b> Blueprints (as-designed) live in CAD files while physical jobsites (as-built) evolve dynamically, creating an unmonitored information chasm.", bullet_style))
    story.append(Paragraph("• <b>Unforeseen Timeline Cascades:</b> Missing structural prerequisites (e.g. curing slabs or misplaced columns) cause cascading delays across subcontractors, triggering massive contractual penalties.", bullet_style))
    story.append(Paragraph("• <b>Safety and Compliance Blind Spots:</b> Workers operating without PPE or structural deviations going unflagged lead to hazardous site conditions.", bullet_style))

    story.append(Spacer(1, 8))

    # Section 2: What is BuildVerse AI
    story.append(Paragraph("2. About BuildVerse AI", h1_style))
    story.append(Paragraph(
        "<b>BuildVerse AI</b> is an intelligent, integrated end-to-end Digital Twin platform and automated site management operating system. "
        "It acts as a unified central nervous system that spans the entire project lifecycle—from parametric 2D architectural space generation "
        "to computer-vision-driven progress detection, live 3D Digital Twin element synchronization, and executive EVM reporting.",
        body_style
    ))

    # Modules Table
    story.append(Paragraph("Core Platform Modules", h2_style))
    modules_data = [
        [Paragraph("Module", table_hdr_style), Paragraph("Scope", table_hdr_style), Paragraph("Core Functionality", table_hdr_style)],
        [
            Paragraph("<b>01 Home</b>", table_cell_bold),
            Paragraph("Portal", table_cell_style),
            Paragraph("Interactive welcome dashboard, system architecture diagram, and capability overview.", table_cell_style)
        ],
        [
            Paragraph("<b>02 Project Details</b>", table_cell_bold),
            Paragraph("Configuration", table_cell_style),
            Paragraph("Multi-project database configuration: plot dimensions, budget limits, workforce quotas, and climate factors.", table_cell_style)
        ],
        [
            Paragraph("<b>03 AI Floor Planner</b>", table_cell_bold),
            Paragraph("Architectural CAD", table_cell_style),
            Paragraph("Generates 2D vector floor blueprints, enforces building-code room dimension validation, and renders 3D room geometries.", table_cell_style)
        ],
        [
            Paragraph("<b>04 Construction Schedule</b>", table_cell_bold),
            Paragraph("CPM Planning", table_cell_style),
            Paragraph("Algorithmic 12-phase construction scheduling (Foundation to Finishing) with interactive Plotly Gantt charts, labor and material estimators.", table_cell_style)
        ],
        [
            Paragraph("<b>05 Digital Twin</b>", table_cell_bold),
            Paragraph("3D Replica", table_cell_style),
            Paragraph("WebGL-powered 3D spatial replica synchronizing real-time phase completion states (Completed, In-Progress, Pending).", table_cell_style)
        ],
        [
            Paragraph("<b>06 Daily Progress</b>", table_cell_bold),
            Paragraph("AI Vision Engine", table_cell_style),
            Paragraph("Ingests site images, video feeds, and drone footage. Uses OpenCV/YOLO to detect structural elements, calculate completed vs. missing work %, and flag safety hazards.", table_cell_style)
        ],
        [
            Paragraph("<b>07 AI Reports</b>", table_cell_bold),
            Paragraph("Automated Audits", table_cell_style),
            Paragraph("Generates executive summary audits, predictive delay explanations, and downloadable ReportLab PDF inspection reports.", table_cell_style)
        ],
        [
            Paragraph("<b>08 Dashboard</b>", table_cell_bold),
            Paragraph("Executive KPIs", table_cell_style),
            Paragraph("Tracks Earned Value Management (EVM), budget burn rates, S-Curves, schedule variance, and real-time risk indicators.", table_cell_style)
        ]
    ]

    mod_table = Table(modules_data, colWidths=[110, 84, 310])
    mod_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), table_header_bg),
        ('BOX', (0, 0), (-1, -1), 0.5, border_cyan),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, row_alt_bg]),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(mod_table)

    story.append(PageBreak())

    # Section 3: Usage & End-to-End Workflow
    story.append(Paragraph("3. Operational Usage & Workflow", h1_style))
    story.append(Paragraph(
        "BuildVerse AI operates through a cohesive 5-stage closed feedback loop:",
        body_style
    ))

    stages = [
        ("Stage 1: Project Initiation & Boundary Definition",
         "The project engineer registers plot coordinates, boundary units, budget caps, expected workforce availability, and regional weather parameters in Module 02."),
        ("Stage 2: AI Floor Plan Generation & Validation",
         "In Module 03, parametric dimensions are allocated for master bedrooms, living halls, kitchens, and utilities. The built-in dimension validator checks setbacks, door/window ratios, and livability codes before generating 2D vector plans and 3D preview meshes."),
        ("Stage 3: 12-Phase CPM Timeline & Resource Estimation",
         "In Module 04, the system calculates critical path dependencies across standard phases (Foundation, Columns, Beams, Slab, Brick Work, Plastering, Electrical, Plumbing, Flooring, Painting, Interior, Finishing). Material quantities (cement bags, steel metric tons, sand cubic feet) and labor crew sizes are automatically estimated."),
        ("Stage 4: Automated Site Media Ingestion & Computer Vision",
         "In Module 06, field personnel upload site photos, timelapse videos, or drone photogrammetry. The computer vision pipeline applies contour analysis, edge detection, and structural object segmentation to compare observed site progress against planned milestones, deriving exact completion percentages and delay metrics."),
        ("Stage 5: Live Digital Twin Synchronisation & Executive Governance",
         "In Modules 05, 07, and 08, the 3D Digital Twin updates its structural state in real time. Executive teams review S-Curves, EVM indicators, and automated AI audit recommendations, triggering instant PDF export for client and regulatory compliance.")
    ]

    for title, desc in stages:
        story.append(Paragraph(f"<b>{title}</b>", h2_style))
        story.append(Paragraph(desc, body_style))

    story.append(Spacer(1, 10))

    # Section 4: Software Requirements & Detailed Justification
    story.append(Paragraph("4. Software Requirements & Technology Rationale", h1_style))
    story.append(Paragraph(
        "Every technology and dependency in BuildVerse AI was purposefully chosen to optimize performance, eliminate unnecessary software licensing fees, and deliver an intuitive real-time experience.",
        body_style
    ))

    tech_specs = [
        [Paragraph("Technology", table_hdr_style), Paragraph("Role", table_hdr_style), Paragraph("Why We Are Using It (Justification)", table_hdr_style)],
        [
            Paragraph("<b>Python 3.11</b>", table_cell_bold),
            Paragraph("Core Language", table_cell_style),
            Paragraph("Provides rich mathematical, vision, and AI library support. Python 3.11 delivers up to 25% faster execution compared to older versions, crucial for image array transformations.", table_cell_style)
        ],
        [
            Paragraph("<b>Streamlit</b>", table_cell_bold),
            Paragraph("Web UI Framework", table_cell_style),
            Paragraph("Enables a reactive, data-dense interface directly in Python without complex Node.js/React build pipelines. Fast UI updates and instant session-state management.", table_cell_style)
        ],
        [
            Paragraph("<b>Plotly & WebGL</b>", table_cell_bold),
            Paragraph("2D/3D Data Viz", table_cell_style),
            Paragraph("Renders high-performance interactive 3D Digital Twin models, zoomable Gantt timelines, and S-Curves in the browser with full rotation, pan, and hover telemetry.", table_cell_style)
        ],
        [
            Paragraph("<b>OpenCV (Headless)</b>", table_cell_bold),
            Paragraph("Computer Vision", table_cell_style),
            Paragraph("Performs real-time frame extraction from video/drone feeds, Canny edge detection, contour area measurement, and structural alignment without requiring GPU dependencies.", table_cell_style)
        ],
        [
            Paragraph("<b>Pillow (PIL)</b>", table_cell_bold),
            Paragraph("Image Processing", table_cell_style),
            Paragraph("Provides robust image normalization, format conversion, thumbnail generation, and metadata extraction for all user-uploaded site media.", table_cell_style)
        ],
        [
            Paragraph("<b>Pandas & NumPy</b>", table_cell_bold),
            Paragraph("Numerical Engine", table_cell_style),
            Paragraph("High-speed vector and matrix computations for timeline date offsets, labor cost distribution curves, EVM math, and 3D coordinate mesh manipulation.", table_cell_style)
        ],
        [
            Paragraph("<b>ReportLab</b>", table_cell_bold),
            Paragraph("PDF Generation", table_cell_style),
            Paragraph("Generates pixel-perfect, printable, executive-grade PDF audit documents with dynamic tables, multi-page canvases, and branded headers/footers.", table_cell_style)
        ],
        [
            Paragraph("<b>SQLite & Pydantic</b>", table_cell_bold),
            Paragraph("Database & Schema", table_cell_style),
            Paragraph("Zero-configuration, serverless embedded database requiring no cloud setup or server maintenance, paired with Pydantic for strict runtime type validation.", table_cell_style)
        ],
        [
            Paragraph("<b>FastAPI & Uvicorn</b>", table_cell_bold),
            Paragraph("REST API Service", table_cell_style),
            Paragraph("Provides high-throughput asynchronous endpoints allowing automated edge devices, drone stations, and mobile apps to stream inspection data directly into BuildVerse.", table_cell_style)
        ]
    ]

    tech_table = Table(tech_specs, colWidths=[95, 85, 324])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), table_header_bg),
        ('BOX', (0, 0), (-1, -1), 0.5, border_cyan),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, row_alt_bg]),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(tech_table)

    story.append(PageBreak())

    # Section 5: Strategic Impact & Key Benefits
    story.append(Paragraph("5. Business Value & Strategic Impact", h1_style))
    story.append(Paragraph(
        "Implementing BuildVerse AI delivers immediate measurable advantages across all operational dimensions:",
        body_style
    ))

    story.append(Paragraph("• <b>Elimination of Expensive BIM Overhead:</b> Replaces costly commercial BIM subscriptions ($3,000+/seat/year) with an open, accessible Python-powered digital twin architecture.", bullet_style))
    story.append(Paragraph("• <b>Real-Time Truth & Zero Guesswork:</b> Replaces subjective weekly reports with automated computer vision verification, reducing dispute resolution time between owners and contractors.", bullet_style))
    story.append(Paragraph("• <b>Proactive Risk Prevention:</b> Automated EVM analytics alert site supervisors to schedule drift (SV) and cost variance (CV) days before milestones are compromised.", bullet_style))
    story.append(Paragraph("• <b>Enhanced Safety & Defect Accountability:</b> Instant visual flagging of missing structural components or safety compliance lapses protects workers and minimizes expensive structural rework.", bullet_style))
    story.append(Paragraph("• <b>One-Click Enterprise Audits:</b> Instantaneous generation of standardized PDF reports for investors, financial institutions, and municipal regulatory boards.", bullet_style))

    story.append(Spacer(1, 14))

    # Callout Box
    conclusion_data = [[
        Paragraph(
            "<b>Conclusion:</b> BuildVerse AI modernizes civil engineering by fusing computational floor planning, automated scheduling, "
            "computer vision surveillance, and 3D digital twins into a single cohesive platform. It empowers construction stakeholders to "
            "build faster, safer, and strictly within budget.",
            banner_style
        )
    ]]
    conclusion_table = Table(conclusion_data, colWidths=[504])
    conclusion_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), light_cyan_bg),
        ('BOX', (0, 0), (-1, -1), 1.5, primary_cyan),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(conclusion_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully generated at: {output_path}")

if __name__ == "__main__":
    out_dir = Path(r"d:\projects\prudvi(construction)\uploads\reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "BuildVerse_AI_Project_Documentation.pdf"
    generate_pdf(target)

    # Also make a copy directly in project root for easy user access
    root_target = Path(r"d:\projects\prudvi(construction)\BuildVerse_AI_Project_Documentation.pdf")
    generate_pdf(root_target)
