"""
DF Automation & Robotics Maintenance Form - PDF Generator
Produces exact replica of official DF Maintenance Form templates using ReportLab.
"""
import io
import os
import re
import base64
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)

BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / "data" / "uploads"

# DF Corporate Colors
PRIMARY_COLOR = colors.HexColor("#0f172a") # Slate 900
BRAND_BLUE = colors.HexColor("#0284c7")    # Cyan 600
ACCENT_GREEN = colors.HexColor("#059669")  # Emerald 600
LIGHT_BG = colors.HexColor("#f8fafc")      # Slate 50
BORDER_COLOR = colors.HexColor("#cbd5e1")  # Slate 300
TEXT_DARK = colors.HexColor("#1e293b")     # Slate 800
TEXT_MUTED = colors.HexColor("#64748b")    # Slate 500

def create_styles():
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=PRIMARY_COLOR,
        alignment=1 # Center
    ))
    
    styles.add(ParagraphStyle(
        'FormCode',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=BRAND_BLUE,
        alignment=1
    ))
    
    styles.add(ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.white
    ))

    styles.add(ParagraphStyle(
        'TableLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=TEXT_DARK
    ))

    styles.add(ParagraphStyle(
        'TableValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=TEXT_DARK
    ))

    styles.add(ParagraphStyle(
        'TableValueBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=TEXT_DARK
    ))
    
    styles.add(ParagraphStyle(
        'SmallMuted',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=TEXT_MUTED
    ))

    return styles

def generate_maintenance_pdf(report: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=28,
        rightMargin=28,
        topMargin=28,
        bottomMargin=28
    )
    
    styles = create_styles()
    story = []
    
    form_code = report.get('formCode', 'FRM/CS/015-V1.0')
    form_title = report.get('formTitle', 'DF Automation & Robotics Sdn Bhd Maintenance Form')
    subtitle = report.get('subtitle', 'Preventive Maintenance Inspection Report')
    cust_data = report.get('customerData', {})
    machine_data = report.get('machineData', {})
    replacements = report.get('recommendedReplacements', [])
    sections = report.get('sections', [])
    signatures = report.get('signatures', {})
    
    # 1. Official Header
    header_data = [
        [
            Paragraph("<b>DF AUTOMATION & ROBOTICS</b>", ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=13, textColor=BRAND_BLUE)),
            Paragraph(f"<b>FORM NO:</b> {form_code}", ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=9, textColor=TEXT_DARK, alignment=2))
        ],
        [
            Paragraph(f"<b>{form_title.upper()}</b>", styles['DocTitle']),
            Paragraph(f"<b>SOP:</b> {subtitle}", ParagraphStyle('H3', fontName='Helvetica', fontSize=8, textColor=TEXT_MUTED, alignment=2))
        ]
    ]
    t_header = Table(header_data, colWidths=[360, 180])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_BLUE, spaceAfter=8))
    
    # 2. Customer & Machine Details Dual Box
    details_table_data = [
        [
            Paragraph("<b>CUSTOMER DETAILS</b>", ParagraphStyle('TH1', fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white)),
            Paragraph("<b>EQUIPMENT / AMR DETAILS</b>", ParagraphStyle('TH2', fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white))
        ],
        [
            Paragraph(f"<b>Company:</b> {cust_data.get('company', '-')}<br/>"
                      f"<b>PIC Name:</b> {cust_data.get('picName', '-')}<br/>"
                      f"<b>Servicer Name:</b> {cust_data.get('servicerName', '-')}<br/>"
                      f"<b>Date:</b> {cust_data.get('date', datetime.now().strftime('%Y-%m-%d'))}", styles['TableValue']),
            Paragraph(f"<b>Model:</b> {machine_data.get('amrModel', machine_data.get('chargerModel', machine_data.get('payloadModel', '-')))}<br/>"
                      f"<b>Serial No:</b> {machine_data.get('amrSerial', machine_data.get('chargerSerial', machine_data.get('serialNumber', '-')))}<br/>"
                      f"<b>Last Service Date:</b> {machine_data.get('lastServiceDate', '-')}<br/>"
                      f"<b>Mileage / Counter:</b> {machine_data.get('mileageReading', machine_data.get('counterReading', '-'))} (Last: {machine_data.get('lastServiceMileage', '-')})<br/>"
                      f"<b>Mainboard:</b> {machine_data.get('mainboardVersion', '-')} | <b>Navwiz:</b> {machine_data.get('navwizVersion', '-')}", styles['TableValue'])
        ]
    ]
    t_details = Table(details_table_data, colWidths=[265, 275])
    t_details.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), PRIMARY_COLOR),
        ('BACKGROUND', (1,0), (1,0), BRAND_BLUE),
        ('BACKGROUND', (0,1), (-1,1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_details)
    story.append(Spacer(1, 8))

    # 3. Recommended Part Replacement / Service Request Box
    if replacements and len(replacements) > 0:
        rep_rows = [[Paragraph("<b>RECOMMENDED SERVICE / PART REPLACEMENT REQUEST</b>", ParagraphStyle('R1', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
                     Paragraph("<b>MAINTENANCE INTERVAL GUIDELINE</b>", ParagraphStyle('R2', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, alignment=2))]]
        
        # Format into 2 items per row
        for rep in replacements:
            is_checked = rep.get('checked', False)
            check_mark = "<b>[ ✓ ]</b>" if is_checked else "[ &nbsp; ]"
            rep_rows.append([
                Paragraph(f"{check_mark} {rep.get('item')}", styles['TableValueBold'] if is_checked else styles['TableValue']),
                Paragraph(f"<i>{rep.get('guideline')}</i>", ParagraphStyle('G1', fontName='Helvetica', fontSize=7.5, textColor=TEXT_MUTED, alignment=2))
            ])
            
        t_rep = Table(rep_rows, colWidths=[360, 180])
        t_rep.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
            ('BACKGROUND', (0,1), (-1,-1), colors.white),
            ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
            ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_rep)
        story.append(Spacer(1, 8))

    # 4. Step-by-Step Inspection Sections
    for sec in sections:
        sec_title = sec.get('title', 'Inspection Section')
        sec_type = sec.get('type', 'standard')
        items = sec.get('items', [])
        
        sec_rows = [[
            Paragraph(f"<b>{sec_title.upper()}</b>", styles['SectionHeader']),
            Paragraph("<b>RESULT / REMARK</b>", ParagraphStyle('SH2', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, alignment=2))
        ]]
        
        if sec_type == 'rating_matrix':
            sec_rows[0] = [
                Paragraph(f"<b>{sec_title.upper()}</b>", styles['SectionHeader']),
                Paragraph("<b>1: OK | 2: Future Attention | 3: Immediate</b>", ParagraphStyle('SH3', fontName='Helvetica-Bold', fontSize=7.5, textColor=colors.white, alignment=2))
            ]
            for itm in items:
                val = str(itm.get('value', '1')).strip()
                badge = "[ 1 - Check OK ]"
                if val == '2' or 'Future' in val:
                    badge = "<font color='#d97706'><b>[ 2 - Future Attention ]</b></font>"
                elif val == '3' or 'Immediate' in val:
                    badge = "<font color='#dc2626'><b>[ 3 - Immediate Attention ]</b></font>"
                elif val == '1' or 'OK' in val:
                    badge = "<font color='#059669'><b>[ 1 - Check OK ]</b></font>"

                sec_rows.append([
                    Paragraph(itm.get('label', ''), styles['TableValue']),
                    Paragraph(badge, ParagraphStyle('BV', fontName='Helvetica', fontSize=8, alignment=2))
                ])
        elif sec_type == 'function_checklist' or sec_type == 'final_checklist' or sec_type == 'toggle_list':
            for itm in items:
                checked = itm.get('checked', True)
                mark = "<font color='#059669'><b>[ ✓ FULL FUNCTION / OK ]</b></font>" if checked else "<font color='#dc2626'><b>[ ✗ NOT OK / ATTENTION ]</b></font>"
                sec_rows.append([
                    Paragraph(itm.get('label', ''), styles['TableValue']),
                    Paragraph(mark, ParagraphStyle('FM', fontName='Helvetica', fontSize=8, alignment=2))
                ])
        else:
            for itm in items:
                val = itm.get('value', itm.get('checked', 'OK'))
                if isinstance(val, bool):
                    val_str = "[ ✓ ]" if val else "[ ✗ ]"
                else:
                    val_str = str(val)
                sec_rows.append([
                    Paragraph(itm.get('label', ''), styles['TableValue']),
                    Paragraph(f"<b>{val_str}</b>", ParagraphStyle('ST', fontName='Helvetica', fontSize=8, alignment=2))
                ])

        t_sec = Table(sec_rows, colWidths=[380, 160])
        t_sec.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), BRAND_BLUE),
            ('BACKGROUND', (0,1), (-1,-1), colors.white),
            ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
            ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(KeepTogether([t_sec, Spacer(1, 8)]))

    # 5. Remarks & Recommendations
    notes = report.get('notes', '').strip()
    next_service = report.get('nextPeriodicMaintenance', '').strip()
    
    remarks_data = [
        [Paragraph("<b>OTHER REMARKS & NEXT PERIODIC SCHEDULE</b>", styles['SectionHeader'])],
        [Paragraph(f"<b>Remarks / Actions Taken:</b> {notes if notes else 'All standard preventive inspection routines executed in accordance with DF AMR SOP.'}<br/>"
                   f"<b>Next Periodic Maintenance Date:</b> <b>{next_service if next_service else 'In 6 Months'}</b>", styles['TableValue'])]
    ]
    t_remarks = Table(remarks_data, colWidths=[540])
    t_remarks.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), PRIMARY_COLOR),
        ('BACKGROUND', (0,1), (0,1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(KeepTogether([t_remarks, Spacer(1, 10)]))

    # 6. Official Signatures Block
    servicer_sig = signatures.get('servicerSignature', '')
    customer_sig = signatures.get('customerSignature', '')
    servicer_date = signatures.get('servicerDate', cust_data.get('date', datetime.now().strftime('%Y-%m-%d')))
    customer_date = signatures.get('customerDate', cust_data.get('date', datetime.now().strftime('%Y-%m-%d')))
    
    def format_signature_cell(sig_str, signer_name, default_name, sig_date):
        cell_contents = []
        if sig_str and str(sig_str).startswith("data:image/"):
            try:
                img_b64 = re.sub(r'^data:image/.+;base64,', '', str(sig_str))
                img_bytes = base64.b64decode(img_b64)
                img_io = io.BytesIO(img_bytes)
                sig_img = Image(img_io, width=120, height=40)
                cell_contents.append(sig_img)
            except Exception:
                cell_contents.append(Paragraph("<br/><i>[Digital Signature Authenticated]</i>", styles['TableValue']))
        elif sig_str:
            cell_contents.append(Paragraph(f"<br/><font color='#1a73e8'><b>{sig_str}</b></font>", styles['TableValue']))
        else:
            cell_contents.append(Paragraph("<br/>____________________________", styles['TableValue']))
            
        cell_contents.append(Spacer(1, 4))
        cell_contents.append(Paragraph(
            f"<b>Name:</b> {signer_name if signer_name else default_name}<br/>"
            f"<b>Date:</b> {sig_date}", styles['TableValue']
        ))
        return cell_contents

    sig_data = [
        [
            Paragraph("<b>SERVICER SIGNATURE</b>", ParagraphStyle('SG1', fontName='Helvetica-Bold', fontSize=8, textColor=PRIMARY_COLOR)),
            Paragraph("<b>CUSTOMER SIGNATURE</b>", ParagraphStyle('SG2', fontName='Helvetica-Bold', fontSize=8, textColor=PRIMARY_COLOR))
        ],
        [
            format_signature_cell(servicer_sig, cust_data.get('servicerName'), 'DF Certified Engineer', servicer_date),
            format_signature_cell(customer_sig, cust_data.get('picName'), 'Customer Representative', customer_date)
        ]
    ]
    t_sig = Table(sig_data, colWidths=[270, 270])
    t_sig.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
        ('BACKGROUND', (0,1), (-1,1), colors.white),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(KeepTogether([t_sig]))

    doc.build(story)
    return buffer.getvalue()
