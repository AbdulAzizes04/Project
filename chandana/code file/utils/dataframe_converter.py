import io
import pandas as pd
from typing import Tuple
from utils.logger import logger

def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """Converts a pandas DataFrame to UTF-8 encoded CSV bytes."""
    return df.to_csv(index=False).encode('utf-8')

def convert_df_to_excel(df: pd.DataFrame) -> bytes:
    """Converts a pandas DataFrame to Excel (.xlsx) bytes."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='QueryResult')
    return output.getvalue()

def convert_df_to_pdf(df: pd.DataFrame, title: str = "SQL Query Result Report", query: str = "") -> bytes:
    """
    Converts a pandas DataFrame into a styled PDF report using ReportLab.
    Falls back gracefully if reportlab is missing.
    """
    try:
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(letter),
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor("#0F172A"),
            spaceAfter=12
        )
        elements.append(Paragraph(title, title_style))
        
        # SQL Query subtext
        if query:
            query_style = ParagraphStyle(
                'QueryStyle',
                parent=styles['Code'],
                fontSize=9,
                textColor=colors.HexColor("#334155"),
                backColor=colors.HexColor("#F1F5F9"),
                borderColor=colors.HexColor("#CBD5E1"),
                borderWidth=1,
                borderPadding=6,
                spaceAfter=14
            )
            elements.append(Paragraph(f"<b>Executed SQL Query:</b><br/>{query}", query_style))

        # Format table data
        # Limit rows for PDF layout if large
        max_pdf_rows = 100
        truncated_df = df.head(max_pdf_rows)
        
        headers = [str(col) for col in truncated_df.columns]
        table_data = [headers]
        
        for _, row in truncated_df.iterrows():
            formatted_row = [str(val) if not pd.isna(val) else "" for val in row.values]
            table_data.append(formatted_row)
            
        pdf_table = Table(table_data, repeatRows=1)
        pdf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(pdf_table)
        
        if len(df) > max_pdf_rows:
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"<i>Note: Showing first {max_pdf_rows} rows out of {len(df)} total rows.</i>", styles['Italic']))

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
        
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        # Fallback simple text buffer
        return f"PDF Export Error: {e}".encode('utf-8')
