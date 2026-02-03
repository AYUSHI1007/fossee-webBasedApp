"""
Generate PDF report for a dataset using ReportLab.
"""
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER


def build_pdf_report(dataset):
    """Build PDF report for given EquipmentDataset. Returns bytes."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=12,
        alignment=TA_CENTER,
    )

    elements = []

    elements.append(Paragraph("Chemical Equipment Parameter Report", title_style))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(f"Dataset: {dataset.name}", styles['Heading2']))
    elements.append(Paragraph(f"Generated: {dataset.created_at.strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("Summary Statistics", styles['Heading2']))
    summary_data = [
        ['Metric', 'Value'],
        ['Total Equipment Count', str(dataset.total_count)],
        ['Average Flowrate', str(dataset.avg_flowrate) if dataset.avg_flowrate is not None else 'N/A'],
        ['Average Pressure', str(dataset.avg_pressure) if dataset.avg_pressure is not None else 'N/A'],
        ['Average Temperature', str(dataset.avg_temperature) if dataset.avg_temperature is not None else 'N/A'],
    ]
    t1 = Table(summary_data, colWidths=[3 * inch, 3 * inch])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    elements.append(t1)
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Equipment Type Distribution", styles['Heading2']))
    dist_data = [['Type', 'Count']]
    for k, v in (dataset.type_distribution or {}).items():
        dist_data.append([str(k), str(v)])
    t2 = Table(dist_data, colWidths=[3 * inch, 2 * inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Data Table (Sample)", styles['Heading2']))
    rows = dataset.raw_rows or []
    if rows:
        headers = list(rows[0].keys())
        table_data = [headers] + [[str(r.get(h, '')) for h in headers] for r in rows[:50]]
        col_width = 4.5 * inch / len(headers) if headers else 1 * inch
        t3 = Table(table_data, colWidths=[col_width] * len(headers))
        t3.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        elements.append(t3)
    else:
        elements.append(Paragraph("No data rows.", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
