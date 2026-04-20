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


# ================= WORD DOC =================
def generate_word_doc(data, root, l2, res):

    doc = Document()

    # ===== TITLE =====
    title = doc.add_heading("INCIDENT REPORT", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.runs[0]
    run.bold = True
    run.font.color.rgb = RGBColor(31, 78, 121)

    # ===== TABLE 1 =====
    table = doc.add_table(rows=4, cols=4)
    table.style = "Table Grid"

    def fill(row, col, key, value):
        h = table.rows[row].cells[col]
        v = table.rows[row].cells[col+1]

        h.text = key.upper()
        shade_cell(h)

        # Bold header
        for r in h.paragraphs[0].runs:
            r.bold = True

        v.text = ""
        p = v.paragraphs[0]

        if key == "Incident":
            add_hyperlink(
                p,
                f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={value}",
                str(value)
            )
        elif key == "Azure Bug":
            add_hyperlink(
                p,
                f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{value}",
                str(value)
            )
        elif key == "PTC Case":
            add_hyperlink(
                p,
                f"https://support.ptc.com/app/caseviewer/?case={value}",
                str(value)
            )
        else:
            p.text = str(value)

    fill(0,0,"Incident",data.get("number"))
    fill(0,2,"Created By",data.get("created_by"))

    fill(1,0,"Azure Bug",data.get("azure_bug"))
    fill(1,2,"Created Date",data.get("created_date"))

    fill(2,0,"PTC Case",data.get("ptc_case"))
    fill(2,2,"Assigned To",data.get("assigned_to"))

    fill(3,0,"Priority",data.get("priority"))
    fill(3,2,"Resolved Date",data.get("resolved_date"))

    doc.add_paragraph("")

    # ===== TABLE 2 =====
    desc_table = doc.add_table(rows=2, cols=2)
    desc_table.style = "Table Grid"

    headers = ["SHORT DESCRIPTION", "DESCRIPTION"]

    for i in range(2):
        cell = desc_table.rows[0].cells[i]
        cell.text = headers[i]
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        shade_cell(cell)

        for r in cell.paragraphs[0].runs:
            r.bold = True

    desc_table.rows[1].cells[0].text = clean_text(data.get("short_description"))
    desc_table.rows[1].cells[1].text = clean_text(data.get("description"))

    # ===== TEXT =====
    doc.add_heading("ROOT CAUSE", 1)
    doc.add_paragraph(root)

    doc.add_heading("L2 ANALYSIS", 1)
    doc.add_paragraph(l2)

    doc.add_heading("RESOLUTION", 1)
    doc.add_paragraph(res)

    # ===== FOOTER =====
    add_footer(doc, data)

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

    def link(url, text):
        return Paragraph(f'<link href="{url}">{text}</link>', styles["Normal"])

    def wrap(text):
        return Paragraph(str(text), styles["Normal"])

    # TABLE 1
    table_data = [
        ["INCIDENT", link(f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={data.get('number')}", data.get("number")),
         "CREATED BY", wrap(data.get("created_by"))],

        ["AZURE BUG", link(f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{data.get('azure_bug')}", data.get("azure_bug")),
         "CREATED DATE", wrap(data.get("created_date"))],

        ["PTC CASE", link(f"https://support.ptc.com/app/caseviewer/?case={data.get('ptc_case')}", data.get("ptc_case")),
         "ASSIGNED TO", wrap(data.get("assigned_to"))],

        ["PRIORITY", wrap(data.get("priority")),
         "RESOLVED DATE", wrap(data.get("resolved_date"))]
    ]

    table = Table(table_data, colWidths=[110, 180, 110, 180])

    table.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('BACKGROUND',(0,0),(0,-1),colors.lightgrey),
        ('BACKGROUND',(2,0),(2,-1),colors.lightgrey),
        ('VALIGN',(0,0),(-1,-1),'TOP')
    ]))

    elements.append(table)
    elements.append(Spacer(1, 10))

    # TABLE 2
    desc = Table([
        ["SHORT DESCRIPTION","DESCRIPTION"],
        [wrap(clean_text(data.get("short_description"))),
         wrap(clean_text(data.get("description")))]
    ], colWidths=[220,280])

    desc.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
        ('VALIGN',(0,0),(-1,-1),'TOP')
    ]))

    elements.append(desc)

    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<b>ROOT CAUSE</b>", styles["Heading2"]))
    elements.append(Paragraph(root, styles["Normal"]))

    elements.append(Paragraph("<b>L2 ANALYSIS</b>", styles["Heading2"]))
    elements.append(Paragraph(l2, styles["Normal"]))

    elements.append(Paragraph("<b>RESOLUTION</b>", styles["Heading2"]))
    elements.append(Paragraph(res, styles["Normal"]))

    # FOOTER
    def footer(canvas, doc):
        canvas.saveState()
        width, height = doc.pagesize

        canvas.drawString(40, 20, data.get("number"))
        canvas.drawCentredString(width/2, 20, f"Page {doc.page}")
        canvas.drawRightString(width-40, 20, data.get("priority"))

        canvas.restoreState()

    doc.build(elements, onFirstPage=footer, onLaterPages=footer)

    buffer.seek(0)
    return buffer

