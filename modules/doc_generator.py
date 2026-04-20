from docx import Document
from docx.shared import RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import re

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


def clean_text(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip()


# ================= WORD =================
def generate_word_doc(data):

    doc = Document()

    # TITLE
    title = doc.add_heading("INCIDENT REPORT", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].font.color.rgb = RGBColor(31, 78, 121)

    # TABLE 1
    table = doc.add_table(rows=4, cols=4)
    table.style = "Table Grid"

    def fill(r, c, key, val):
        table.rows[r].cells[c].text = key.upper()
        table.rows[r].cells[c+1].text = str(val or "")

    fill(0,0,"Incident",data.get("number"))
    fill(0,2,"Created By",data.get("created_by"))

    fill(1,0,"Azure Bug",data.get("azure_bug"))
    fill(1,2,"Created Date",data.get("created_date"))

    fill(2,0,"PTC Case",data.get("ptc_case"))
    fill(2,2,"Assigned To",data.get("assigned_to"))

    fill(3,0,"Priority",data.get("priority"))
    fill(3,2,"Resolved Date",data.get("resolved_date"))

    doc.add_paragraph("")

    # TABLE 2
    desc = doc.add_table(rows=2, cols=2)
    desc.style = "Table Grid"

    desc.columns[0].width = Inches(3)
    desc.columns[1].width = Inches(5)

    desc.rows[0].cells[0].text = "SHORT DESCRIPTION"
    desc.rows[0].cells[1].text = "DESCRIPTION"

    desc.rows[1].cells[0].text = clean_text(data.get("short_description"))
    desc.rows[1].cells[1].text = clean_text(data.get("description"))

    # SECTIONS
    doc.add_heading("ROOT CAUSE", 1)
    doc.add_paragraph(data.get("root", ""))

    doc.add_heading("L2 ANALYSIS", 1)
    doc.add_paragraph(data.get("l2", ""))

    doc.add_heading("RESOLUTION", 1)
    doc.add_paragraph(data.get("res", ""))

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


# ================= PDF =================
def generate_pdf(data):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        leftMargin=30,
        rightMargin=30,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>INCIDENT REPORT</b>", styles["Title"]))
    elements.append(Spacer(1, 10))

    def wrap(x): return Paragraph(str(x or ""), styles["Normal"])

    table = Table([
        ["INCIDENT", wrap(data.get("number")), "CREATED BY", wrap(data.get("created_by"))],
        ["AZURE BUG", wrap(data.get("azure_bug")), "CREATED DATE", wrap(data.get("created_date"))],
        ["PTC CASE", wrap(data.get("ptc_case")), "ASSIGNED TO", wrap(data.get("assigned_to"))],
        ["PRIORITY", wrap(data.get("priority")), "RESOLVED DATE", wrap(data.get("resolved_date"))]
    ], colWidths=[110,180,110,180])

    table.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('BACKGROUND',(0,0),(0,-1),colors.lightgrey),
        ('BACKGROUND',(2,0),(2,-1),colors.lightgrey)
    ]))

    elements.append(table)
    elements.append(Spacer(1, 10))

    desc = Table([
        ["SHORT DESCRIPTION","DESCRIPTION"],
        [wrap(data.get("short_description")), wrap(data.get("description"))]
    ], colWidths=[220,280])

    desc.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('BACKGROUND',(0,0),(-1,0),colors.lightgrey)
    ]))

    elements.append(desc)

    doc.build(elements)
    buffer.seek(0)
    return buffer
