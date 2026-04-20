from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import re

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


# ================= CLEAN TEXT =================
def clean_text(text):
    if not text:
        return ""
    return re.sub(
        r"How does the user want.*?\d+",
        "",
        str(text),
        flags=re.IGNORECASE
    ).strip()


# ================= WORD =================
def generate_word_doc(data, root, l2, res, images=None):

    doc = Document()

    # TITLE
    title = doc.add_heading("INCIDENT REPORT", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].bold = True

    # TABLE 1
    table = doc.add_table(rows=4, cols=4)
    table.style = "Table Grid"

    def fill(r, c, k, v):
        table.rows[r].cells[c].text = k.upper()
        table.rows[r].cells[c+1].text = str(v)

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
    t2 = doc.add_table(rows=2, cols=2)
    t2.style = "Table Grid"

    t2.rows[0].cells[0].text = "SHORT DESCRIPTION"
    t2.rows[0].cells[1].text = "DESCRIPTION"

    t2.rows[1].cells[0].text = clean_text(data.get("short_description"))
    t2.rows[1].cells[1].text = clean_text(data.get("description"))

    # ROOT
    doc.add_heading("ROOT CAUSE", 1)
    doc.add_paragraph(root or "")

    if images and images.get("root"):
        doc.add_picture(images["root"], width=Inches(5))

    # L2
    doc.add_heading("L2 ANALYSIS", 1)
    doc.add_paragraph(l2 or "")

    if images and images.get("l2"):
        doc.add_picture(images["l2"], width=Inches(5))

    # RESOLUTION
    doc.add_heading("RESOLUTION", 1)
    doc.add_paragraph(res or "")

    if images and images.get("res"):
        doc.add_picture(images["res"], width=Inches(5))

    # FOOTER (SAFE)
    section = doc.sections[0]
    footer = section.footer.paragraphs[0]
    footer.text = f"{data.get('number')} | {data.get('priority')}"

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer


# ================= PDF =================
def generate_pdf(data, root, l2, res, images=None):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    elements = []

    # TITLE
    elements.append(Paragraph("<b>INCIDENT REPORT</b>", styles["Title"]))
    elements.append(Spacer(1, 10))

    def wrap(x):
        return Paragraph(str(x), styles["Normal"])

    # TABLE 1
    table = Table([
        ["INCIDENT", wrap(data["number"]), "CREATED BY", wrap(data["created_by"])],
        ["AZURE BUG", wrap(data["azure_bug"]), "CREATED DATE", wrap(data["created_date"])],
        ["PTC CASE", wrap(data["ptc_case"]), "ASSIGNED TO", wrap(data["assigned_to"])],
        ["PRIORITY", wrap(data["priority"]), "RESOLVED DATE", wrap(data["resolved_date"])]
    ], colWidths=[90,180,90,180])

    table.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('BACKGROUND',(0,0),(0,-1),colors.lightgrey),
        ('BACKGROUND',(2,0),(2,-1),colors.lightgrey),
    ]))

    elements.append(table)
    elements.append(Spacer(1,10))

    # DESC TABLE
    desc = Table([
        ["SHORT DESCRIPTION","DESCRIPTION"],
        [wrap(clean_text(data["short_description"])),
         wrap(clean_text(data["description"]))]
    ], colWidths=[220,280])

    desc.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
    ]))

    elements.append(desc)

    elements.append(Spacer(1,10))

    # ROOT
    elements.append(Paragraph("<b>ROOT CAUSE</b>", styles["Heading2"]))
    elements.append(Paragraph(root or "", styles["Normal"]))

    if images and images.get("root"):
        elements.append(Image(images["root"], width=400, height=200))

    # L2
    elements.append(Paragraph("<b>L2 ANALYSIS</b>", styles["Heading2"]))
    elements.append(Paragraph(l2 or "", styles["Normal"]))

    if images and images.get("l2"):
        elements.append(Image(images["l2"], width=400, height=200))

    # RES
    elements.append(Paragraph("<b>RESOLUTION</b>", styles["Heading2"]))
    elements.append(Paragraph(res or "", styles["Normal"]))

    if images and images.get("res"):
        elements.append(Image(images["res"], width=400, height=200))

    # FOOTER
    def footer(canvas, doc):
        canvas.drawString(40, 20, data["number"])
        canvas.drawRightString(550, 20, data["priority"])

    doc.build(elements, onFirstPage=footer, onLaterPages=footer)

    buffer.seek(0)
    return buffer
