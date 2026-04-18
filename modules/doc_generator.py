from docx import Document
from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


# ================= WORD =================
def generate_word_doc(data, root, l2, res):

    doc = Document()
    doc.add_heading('INCIDENT REPORT', 0)

    table = doc.add_table(rows=10, cols=2)
    table.style = 'Table Grid'

    rows = [
        ("Incident", data.get("number")),
        ("Azure Bug", data.get("azure_bug")),
        ("PTC Case", data.get("ptc_case")),
        ("Priority", data.get("priority")),
        ("Created By", data.get("created_by")),
        ("Created Date", data.get("created_date")),
        ("Assigned To", data.get("assigned_to")),
        ("Resolved Date", data.get("resolved_date")),
        ("Short Description", data.get("short_description")),
        ("Description", data.get("description")),
    ]

    for i, (k, v) in enumerate(rows):
        table.rows[i].cells[0].text = str(k)
        table.rows[i].cells[1].text = str(v)

    doc.add_heading('Root Cause', 1)
    doc.add_paragraph(root)

    doc.add_heading('L2 Analysis', 1)
    doc.add_paragraph(l2)

    doc.add_heading('Resolution', 1)
    doc.add_paragraph(res)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer


# ================= PDF =================
def generate_pdf(data, root, l2, res):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    table_data = [
        ["Incident", data.get("number")],
        ["Azure Bug", data.get("azure_bug")],
        ["PTC Case", data.get("ptc_case")],
        ["Priority", data.get("priority")],
        ["Created By", data.get("created_by")],
        ["Created Date", data.get("created_date")],
        ["Assigned To", data.get("assigned_to")],
        ["Resolved Date", data.get("resolved_date")],
        ["Short Description", data.get("short_description")],
        ["Description", data.get("description")],
    ]

    table = Table(table_data)
    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey)
    ]))

    elements = [table]

    elements.append(Paragraph("<b>Root Cause</b>", styles["Heading2"]))
    elements.append(Paragraph(root, styles["Normal"]))

    elements.append(Paragraph("<b>L2 Analysis</b>", styles["Heading2"]))
    elements.append(Paragraph(l2, styles["Normal"]))

    elements.append(Paragraph("<b>Resolution</b>", styles["Heading2"]))
    elements.append(Paragraph(res, styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)

    return buffer
