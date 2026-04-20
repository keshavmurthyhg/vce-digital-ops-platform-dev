from docx import Document
from docx.shared import Inches, RGBColor, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from io import BytesIO
import re

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter


# ---------------- COMMON ---------------- #

def clean_text(text):
    if not text:
        return ""
    return re.sub(r"How does the user want.*?\d+", "", str(text), flags=re.I).strip()


# ---------------- WORD ---------------- #

def add_hyperlink(paragraph, url, text):
    part = paragraph.part
    r_id = part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True
    )
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)

    run = OxmlElement("w:r")
    text_elem = OxmlElement("w:t")
    text_elem.text = text
    run.append(text_elem)
    hyperlink.append(run)

    paragraph._p.append(hyperlink)


def set_cell_bg(cell, color="D9D9D9"):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def generate_word_doc(data, root, l2, res, images=None):
    doc = Document()

    # TITLE
    title = doc.add_heading("INCIDENT REPORT", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # TABLE 1
    table = doc.add_table(rows=4, cols=4)
    table.style = "Table Grid"
    table.autofit = False

    widths = [1.5, 2.5, 1.5, 2.5]
    for i, w in enumerate(widths):
        for row in table.rows:
            row.cells[i].width = Inches(w)

    def fill(r, c, key, val):
        h = table.rows[r].cells[c]
        v = table.rows[r].cells[c + 1]

        # HEADER
        p = h.paragraphs[0]
        p.text = key.upper()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for run in p.runs:
            run.bold = True
        set_cell_bg(h)

        # VALUE
        p = v.paragraphs[0]
        if key == "Incident":
            add_hyperlink(p, f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={val}", str(val))
        elif key == "Azure Bug":
            add_hyperlink(p, f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{val}", str(val))
        elif key == "PTC Case":
            add_hyperlink(p, f"https://support.ptc.com/app/caseviewer/?case={val}", str(val))
        else:
            p.text = str(val)

    fill(0, 0, "Incident", data.get("number"))
    fill(0, 2, "Created By", data.get("created_by"))
    fill(1, 0, "Azure Bug", data.get("azure_bug"))
    fill(1, 2, "Created Date", data.get("created_date"))
    fill(2, 0, "PTC Case", data.get("ptc_case"))
    fill(2, 2, "Assigned To", data.get("assigned_to"))
    fill(3, 0, "Priority", data.get("priority"))
    fill(3, 2, "Resolved Date", data.get("resolved_date"))

    doc.add_paragraph("")

    # TABLE 2
    t2 = doc.add_table(rows=2, cols=2)
    t2.style = "Table Grid"
    t2.autofit = False

    for row in t2.rows:
        row.cells[0].width = Inches(3)
        row.cells[1].width = Inches(3)

    headers = ["SHORT DESCRIPTION", "DESCRIPTION"]

    for i, text in enumerate(headers):
        cell = t2.rows[0].cells[i]
        p = cell.paragraphs[0]
        p.text = text
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.bold = True
        set_cell_bg(cell)

    t2.rows[1].cells[0].text = clean_text(data.get("short_description"))
    t2.rows[1].cells[1].text = clean_text(data.get("description"))

    # SECTIONS
    for title, content in [("ROOT CAUSE", root), ("L2 ANALYSIS", l2), ("RESOLUTION", res)]:
        doc.add_heading(title, 1)
        doc.add_paragraph(content if content else "")

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


# ---------------- PDF ---------------- #

def generate_pdf(data, root, l2, res, images=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>INCIDENT REPORT</b>", styles["Title"]))
    elements.append(Spacer(1, 10))

    def link(url, text):
        return Paragraph(f'<link href="{url}" color="blue">{text}</link>', styles["Normal"])

    def wrap(x):
        return Paragraph(str(x), styles["Normal"])

    # TABLE 1
    table = Table([
        ["INCIDENT", link(f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={data.get('number')}", data.get('number')),
         "CREATED BY", wrap(data.get('created_by'))],

        ["AZURE BUG", link(f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{data.get('azure_bug')}", data.get('azure_bug')),
         "CREATED DATE", wrap(data.get('created_date'))],

        ["PTC CASE", link(f"https://support.ptc.com/app/caseviewer/?case={data.get('ptc_case')}", data.get('ptc_case')),
         "ASSIGNED TO", wrap(data.get('assigned_to'))],

        ["PRIORITY", wrap(data.get('priority')),
         "RESOLVED DATE", wrap(data.get('resolved_date'))]
    ], colWidths=[100, 170, 100, 170])

    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),

        # Header columns grey
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),

        # Header formatting
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),

        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 15))

    # TABLE 2
    desc_table = Table([
        ["SHORT DESCRIPTION", "DESCRIPTION"],
        [wrap(clean_text(data.get("short_description"))), wrap(clean_text(data.get("description")))]
    ], colWidths=[260, 260])

    desc_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    elements.append(desc_table)
    elements.append(Spacer(1, 15))

    # SECTIONS
    for title, content in [("ROOT CAUSE", root), ("L2 ANALYSIS", l2), ("RESOLUTION", res)]:
        elements.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
        elements.append(Paragraph(content if content else "", styles["Normal"]))
        elements.append(Spacer(1, 10))

    doc.build(elements)
    buffer.seek(0)
    return buffer
