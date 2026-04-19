from docx import Document
from io import BytesIO

from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


# ================= WORD HYPERLINK =================
def add_hyperlink(paragraph, url, text):
    part = paragraph.part
    r_id = part.relate_to(url, RT.HYPERLINK, is_external=True)

    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)

    run = OxmlElement('w:r')
    run.text = text

    hyperlink.append(run)
    paragraph._p.append(hyperlink)


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

        p = table.rows[i].cells[1].paragraphs[0]

        if k == "Incident":
            add_hyperlink(p, f"https://volvoitsm.service-now.com/{v}", str(v))

        elif k == "Azure Bug":
            add_hyperlink(p, f"https://dev.azure.com/.../{v}", str(v))

        elif k == "PTC Case":
            add_hyperlink(p, f"https://support.ptc.com/app/caseviewer/?case={v}", str(v))

        else:
            p.text = str(v)

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

    def link(url, text):
        return f'<link href="{url}">{text}</link>'

    table_data = [
        ["Incident", Paragraph(link(f"https://volvoitsm.service-now.com/{data.get('number')}", data.get("number")), styles["Normal"])],
        ["Azure Bug", Paragraph(link(f"https://dev.azure.com/.../{data.get('azure_bug')}", data.get("azure_bug")), styles["Normal"])],
        ["PTC Case", Paragraph(link(f"https://support.ptc.com/app/caseviewer/?case={data.get('ptc_case')}", data.get("ptc_case")), styles["Normal"])],
        ["Priority", data.get("priority")],
        ["Created By", data.get("created_by")],
        ["Created Date", data.get("created_date")],
        ["Assigned To", data.get("assigned_to")],
        ["Resolved Date", data.get("resolved_date")],
        ["Short Description", data.get("short_description")],
        ["Description", data.get("description")],
    ]

    table = Table(table_data, colWidths=[150, 350])  # ✅ FIX layout

    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
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
