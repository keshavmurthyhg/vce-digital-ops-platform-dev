from docx import Document
from io import BytesIO
import re

from docx.enum.text import WD_ALIGN_PARAGRAPH

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


# ================= CLEAN DESCRIPTION =================
def clean_text(text):
    if not text:
        return ""
    text = re.sub(
        r"How does the user want to be contacted.*?(\+?\d[\d\s]+)",
        "",
        str(text),
        flags=re.IGNORECASE
    )
    return text.strip()


# ================= WORD =================
def generate_word_doc(data, root, l2, res):

    doc = Document()

    # TITLE
    title = doc.add_heading("INCIDENT REPORT", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # TABLE (2 COLUMN STYLE)
    table = doc.add_table(rows=6, cols=4)
    table.style = 'Table Grid'

    def set_cell(row, col, key, value):
        table.rows[row].cells[col].text = key.upper()
        table.rows[row].cells[col+1].text = str(value)

    set_cell(0, 0, "Incident", data.get("number"))
    set_cell(0, 2, "Created By", data.get("created_by"))

    set_cell(1, 0, "Azure Bug", data.get("azure_bug"))
    set_cell(1, 2, "Created Date", data.get("created_date"))

    set_cell(2, 0, "PTC Case", data.get("ptc_case"))
    set_cell(2, 2, "Assigned To", data.get("assigned_to"))

    set_cell(3, 0, "Priority", data.get("priority"))
    set_cell(3, 2, "Resolved Date", data.get("resolved_date"))

    # DESCRIPTION TABLE
    desc_table = doc.add_table(rows=2, cols=2)
    desc_table.style = 'Table Grid'

    desc_table.rows[0].cells[0].text = "SHORT DESCRIPTION"
    desc_table.rows[0].cells[1].text = "DESCRIPTION"

    desc_table.rows[1].cells[0].text = clean_text(data.get("short_description"))
    desc_table.rows[1].cells[1].text = clean_text(data.get("description"))

    # TEXT
    doc.add_heading("ROOT CAUSE", 1)
    doc.add_paragraph(root)

    doc.add_heading("L2 ANALYSIS", 1)
    doc.add_paragraph(l2)

    doc.add_heading("RESOLUTION", 1)
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

    elements = []

    # TITLE
    elements.append(Paragraph("<b>INCIDENT REPORT</b>", styles["Title"]))
    elements.append(Spacer(1, 10))

    # LINKS
    def link(url, text):
        return Paragraph(f'<link href="{url}">{text}</link>', styles["Normal"])

    table_data = [
        ["INCIDENT", link(f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={data.get('number')}", data.get("number")),
         "CREATED BY", data.get("created_by")],

        ["AZURE BUG", link(f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{data.get('azure_bug')}", data.get("azure_bug")),
         "CREATED DATE", data.get("created_date")],

        ["PTC CASE", link(f"https://support.ptc.com/app/caseviewer/?case={data.get('ptc_case')}", data.get("ptc_case")),
         "ASSIGNED TO", data.get("assigned_to")],

        ["PRIORITY", data.get("priority"),
         "RESOLVED DATE", data.get("resolved_date")]
    ]

    table = Table(table_data, colWidths=[120, 180, 120, 180])

    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))

    elements.append(table)
    elements.append(Spacer(1, 10))

    # DESCRIPTION
    desc_table = Table([
        ["SHORT DESCRIPTION", "DESCRIPTION"],
        [clean_text(data.get("short_description")), clean_text(data.get("description"))]
    ], colWidths=[200, 300])

    desc_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))

    elements.append(desc_table)

    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<b>ROOT CAUSE</b>", styles["Heading2"]))
    elements.append(Paragraph(root, styles["Normal"]))

    elements.append(Paragraph("<b>L2 ANALYSIS</b>", styles["Heading2"]))
    elements.append(Paragraph(l2, styles["Normal"]))

    elements.append(Paragraph("<b>RESOLUTION</b>", styles["Heading2"]))
    elements.append(Paragraph(res, styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)

    return buffer
