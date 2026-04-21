from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import re


def clean_text(text):
    return re.sub(r"How does the user want.*?\d+", "", str(text), flags=re.I).strip()


def generate_pdf(data, root, l2, res):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, leftMargin=40, rightMargin=40)

    styles = getSampleStyleSheet()
    elements = []

    def p(x): return Paragraph(str(x), styles["Normal"])

    elements.append(Paragraph("<b>INCIDENT REPORT</b>", styles["Title"]))
    elements.append(Spacer(1,10))

    table = Table([
        ["INCIDENT", p(data.get("number")), "CREATED BY", p(data.get("created_by"))],
        ["AZURE BUG", p(data.get("azure_bug")), "CREATED DATE", p(data.get("created_date"))],
        ["PTC CASE", p(data.get("ptc_case")), "ASSIGNED TO", p(data.get("assigned_to"))],
        ["PRIORITY", p(data.get("priority")), "RESOLVED DATE", p(data.get("resolved_date"))],
    ], colWidths=[110,170,110,170])

    table.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('BACKGROUND',(0,0),(0,-1),colors.lightgrey),
        ('BACKGROUND',(2,0),(2,-1),colors.lightgrey),
    ]))

    elements.append(table)
    elements.append(Spacer(1,10))

    desc = Table([
        ["SHORT DESCRIPTION", "DESCRIPTION"],
        [p(clean_text(data.get("short_description"))),
         p(clean_text(data.get("description")))]
    ], colWidths=[220,340])

    desc.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
    ]))

    elements.append(desc)

    def footer(canvas, doc):
        canvas.drawString(40,20,data.get("number"))
        canvas.drawCentredString(300,20,f"Page {doc.page}")
        canvas.drawRightString(550,20,data.get("priority"))

    doc.build(elements, onFirstPage=footer, onLaterPages=footer)

    buffer.seek(0)
    return buffer
