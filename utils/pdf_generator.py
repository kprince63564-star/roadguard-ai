"""
ROADGUARD AI - PDF Inspection Report Generator
Generates professional municipal-grade road health and damage inspection reports
using ReportLab.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import io

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    KeepTogether,
    HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from config import REPORTS_DIR, PRIORITY_BANDS

def generate_pdf_report(report_data: Dict[str, Any]) -> str:
    """
    Builds a professional PDF inspection report for the specified damage report.
    Returns the file path to the generated PDF.
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_id = report_data.get("id", "RGD-UNKNOWN")
    clean_id = "".join(c for c in report_id if c.isalnum() or c in ("-", "_"))
    pdf_filename = f"RoadGuard_Report_{clean_id}.pdf"
    pdf_path = REPORTS_DIR / pdf_filename

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    header_style = ParagraphStyle(
        "HeaderTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A")
    )

    subtitle_style = ParagraphStyle(
        "HeaderSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#0284C7")
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#334155")
    )

    body_bold = ParagraphStyle(
        "BodyDarkBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#0F172A")
    )

    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#64748B")
    )

    story = []

    # 1. Header Banner
    header_data = [
        [
            Paragraph("<b>ROADGUARD AI</b>", header_style),
            Paragraph(f"<b>REPORT ID:</b> {report_id}<br/><b>DATE:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", body_style)
        ],
        [
            Paragraph("MUNICIPAL ROAD HEALTH & DAMAGE INTELLIGENCE PLATFORM", subtitle_style),
            Paragraph(f"<b>STATUS:</b> {report_data.get('status', 'New').upper()}", body_bold)
        ]
    ]
    header_table = Table(header_data, colWidths=[380, 160])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0284C7"), spaceAfter=12))

    # 2. Priority & Severity Summary Box
    priority_band = report_data.get("priority_band", "LOW").upper()
    priority_score = float(report_data.get("priority_score", 0.0))
    band_color_hex = PRIORITY_BANDS.get(priority_band, {}).get("color", "#10B981")
    band_color = colors.HexColor(band_color_hex)

    priority_table_data = [
        [
            Paragraph("<b>VISUAL PRIORITY SCORE</b>", body_bold),
            Paragraph("<b>PRIORITY BAND</b>", body_bold),
            Paragraph("<b>PRIMARY DEFECT</b>", body_bold),
            Paragraph("<b>DETECTION COUNT</b>", body_bold)
        ],
        [
            Paragraph(f"<font size=16 color='{band_color_hex}'><b>{priority_score:.1f} / 100</b></font>", body_bold),
            Paragraph(f"<font size=12 color='{band_color_hex}'><b>{priority_band} PRIORITY</b></font>", body_bold),
            Paragraph(f"<b>{report_data.get('primary_class', 'Road Defect')}</b>", body_bold),
            Paragraph(f"<b>{report_data.get('detection_count', 0)} Detected Regions</b>", body_bold)
        ]
    ]
    priority_table = Table(priority_table_data, colWidths=[135, 135, 135, 135])
    priority_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor("#F8FAFC")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(priority_table)
    story.append(Spacer(1, 10))

    # 3. Location & Field Context
    story.append(Paragraph("<b>1. LOCATION & SITE CONTEXT</b>", section_heading))

    lat = report_data.get("latitude")
    lon = report_data.get("longitude")
    coord_text = f"{lat:.5f}, {lon:.5f}" if lat is not None and lon is not None else "Coordinates Not Provided"

    context_data = [
        [Paragraph("<b>Street / Landmark:</b>", body_bold), Paragraph(str(report_data.get("location_address", "Not Specified")), body_style),
         Paragraph("<b>GPS Coordinates:</b>", body_bold), Paragraph(coord_text, body_style)],
        [Paragraph("<b>Location Source:</b>", body_bold), Paragraph(str(report_data.get("location_source", "Not Provided")), body_style),
         Paragraph("<b>Road Classification:</b>", body_bold), Paragraph(str(report_data.get("road_type", "Arterial Road")), body_style)],
        [Paragraph("<b>Traffic Density:</b>", body_bold), Paragraph(str(report_data.get("traffic_volume", "Moderate")), body_style),
         Paragraph("<b>Weather Condition:</b>", body_bold), Paragraph(str(report_data.get("weather_condition", "Dry / Clear")), body_style)],
        [Paragraph("<b>Reporter / Inspector:</b>", body_bold), Paragraph(f"{report_data.get('reporter_name', 'Citizen')} ({report_data.get('reporter_role', 'citizen')})", body_style),
         Paragraph("<b>Recommended Action:</b>", body_bold), Paragraph(str(report_data.get("urgency_level", "Routine")), body_style)]
    ]
    context_table = Table(context_data, colWidths=[120, 150, 120, 150])
    context_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F8FAFC")),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor("#F8FAFC")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(context_table)
    story.append(Spacer(1, 10))

    # 4. Embedded Annotated Imagery (if available)
    annotated_path = report_data.get("annotated_image_path")
    original_path = report_data.get("original_image_path")
    target_img_path = annotated_path if (annotated_path and Path(annotated_path).exists()) else original_path

    if target_img_path and Path(target_img_path).exists():
        story.append(Paragraph("<b>2. VISUAL EVIDENCE & DETECTED REGIONS</b>", section_heading))
        try:
            rl_img = RLImage(str(target_img_path), width=5.5 * inch, height=3.0 * inch)
            img_table = Table([[rl_img]], colWidths=[540])
            img_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#94A3B8")),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ]))
            story.append(img_table)
            caption_text = "AI YOLO Detection Overlay showing annotated bounding boxes and confidence metrics."
            if report_data.get("is_demo_data"):
                caption_text += " [DEMO SIMULATION DATA]"
            story.append(Paragraph(f"<i>{caption_text}</i>", disclaimer_style))
            story.append(Spacer(1, 8))
        except Exception as e:
            story.append(Paragraph(f"Image could not be embedded: {str(e)}", disclaimer_style))

    # 5. Detections Breakdown
    detections = report_data.get("detections", [])
    if detections:
        story.append(Paragraph("<b>3. GRANULAR AI DETECTION BREAKDOWN</b>", section_heading))
        det_rows = [
            [
                Paragraph("<b>#</b>", body_bold),
                Paragraph("<b>Damage Class</b>", body_bold),
                Paragraph("<b>Confidence</b>", body_bold),
                Paragraph("<b>Relative Surface Area</b>", body_bold),
                Paragraph("<b>Bounding Box (x1,y1,x2,y2)</b>", body_bold)
            ]
        ]
        for idx, d in enumerate(detections, 1):
            area_pct = float(d.get("area_ratio", 0.0)) * 100.0
            box_coords = f"({d.get('box_x1',0):.0f}, {d.get('box_y1',0):.0f}, {d.get('box_x2',0):.0f}, {d.get('box_y2',0):.0f})"
            det_rows.append([
                Paragraph(str(idx), body_style),
                Paragraph(str(d.get("class_name", "Damage")), body_style),
                Paragraph(f"{float(d.get('confidence', 0.0))*100:.1f}%", body_style),
                Paragraph(f"{area_pct:.2f}%", body_style),
                Paragraph(box_coords, body_style)
            ])

        det_table = Table(det_rows, colWidths=[25, 155, 75, 115, 170])
        det_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F172A")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(det_table)
        story.append(Spacer(1, 10))

    # 6. Notes & Sign-off Block
    notes = report_data.get("notes") or "No inspector notes attached."
    story.append(Paragraph("<b>4. INSPECTOR NOTES & ACTION DIRECTIVE</b>", section_heading))
    story.append(Paragraph(f"<b>Field Observations:</b> {notes}", body_style))
    story.append(Spacer(1, 8))

    signoff_data = [
        [
            Paragraph("<b>Field Engineer Signature:</b><br/><br/>___________________________", body_style),
            Paragraph("<b>Municipal Approval Officer:</b><br/><br/>___________________________", body_style),
            Paragraph("<b>Target Resolution Date:</b><br/><br/>____ / ____ / 2026", body_style)
        ]
    ]
    signoff_table = Table(signoff_data, colWidths=[180, 180, 180])
    signoff_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(signoff_table)
    story.append(Spacer(1, 12))

    # 7. Disclaimer
    disclaimer_text = (
        "CONFIDENTIAL & OFFICIAL RECORD: ROADGUARD AI generates visual priority assessments using 2D image analysis. "
        "A 2D photograph cannot reliably determine physical depth, subsurface cavitation, or pavement structural load capacity. "
        "All maintenance interventions must be validated by certified municipal civil engineering personnel."
    )
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94A3B8"), spaceAfter=4))
    story.append(Paragraph(disclaimer_text, disclaimer_style))

    doc.build(story)
    return str(pdf_path)
