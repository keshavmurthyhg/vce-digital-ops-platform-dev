from docx import Document
from docx.shared import RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from io import BytesIO
import re

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
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


# ================= HYPERLINK =================
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
    rPr = OxmlElement("w:rPr")

    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rPr.append(u)

    color = OxmlElement("w:color")
    color.set(qn("w:val"), "0000FF")
    rPr.append(color)

    run.append(rPr)

    text_elem = OxmlElement("w:t")
    text_elem.text = str(text)
    run.append(text_elem)

    hyperlink.append(run)
    paragraph._p.append(hyperlink)


def shade_cell(cell):
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), "D9D9D9")
    cell._element.get_or_add_tcPr().append(shading)


# ================= WORD =================
def generate_word_doc(data, root="", l2="", res=""):

    doc = Document()

    title = doc.add_heading("INCIDENT REPORT", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].font.color.rgb = RGBColor(31, 78, 121)

    table = doc.add_table(rows=4, cols=4)
    table.style = "Table Grid"

    def fill(row, col, key, value):
        h = table.rows[row].cells[col]
        v = table.rows[row].cells[col+1]

        h.text = key.upper()
        shade_cell(h)

        for r in h.paragraphs[0].runs:
            r.bold = True

        p = v.paragraphs[0]
        val = str(value or "")

        if key == "Incident":
            add_hyperlink(p,
                f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={val}", val)
        elif key == "Azure Bug":
            add_hyperlink(p,
                f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{val}", val)
        elif key == "PTC Case":
            add_hyperlink(p,
                f"https://support.ptc.com/app/caseviewer/?case={val}", val)
        else:
            p.text = val

    fill(0,0,"Incident",data.get("number"))
    fill(0,2,"Created By",data.get("created_by"))

    fill(1,0,"Azure Bug",data.get("azure_bug"))
    fill(1,2,"Created Date",data.get("created_date"))

    fill(2,0,"PTC Case",data.get("ptc_case"))
    fill(2,2,"Assigned To",data.get("assigned_to"))

    fill(3,0,"Priority",data.get("priority"))
    fill(3,2,"Resolved Date",data.get("resolved_date"))

    doc.add_paragraph("")

    desc = doc.add_table(rows=2, cols=2)
    desc.style = "Table Grid"

    headers = ["SHORT DESCRIPTION", "DESCRIPTION"]

    for i in range(2):
        cell = desc.rows[0].cells[i]
        cell.text = headers[i]
        shade_cell(cell)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in cell.paragraphs[0].runs:
            r.bold = True

    desc.rows[1].cells[0].text = clean_text(data.get("short_description"))
    desc.rows[1].cells[1].text = clean_text(data.get("description"))

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
def generate_pdf(data, root="", l2="", res=""):

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
    def link(url, txt): return Paragraph(f'<link href="{url}">{txt}</link>', styles["Normal"])

    table = Table([
        ["INCIDENT", link(f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={data.get('number')}", data.get("number")),
         "CREATED BY", wrap(data.get("created_by"))],

        ["AZURE BUG", link(f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{data.get('azure_bug')}", data.get("azure_bug")),
         "CREATED DATE", wrap(data.get("created_date"))],

        ["PTC CASE", link(f"https://support.ptc.com/app/caseviewer/?case={data.get('ptc_case')}", data.get("ptc_case")),
         "ASSIGNED TO", wrap(data.get("assigned_to"))],

        ["PRIORITY", wrap(data.get("priority")),
         "RESOLVED DATE", wrap(data.get("resolved_date"))]
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
        [wrap(clean_text(data.get("short_description"))),
         wrap(clean_text(data.get("description")))]
    ], colWidths=[220,280])

    desc.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('BACKGROUND',(0,0),(-1,0),colors.lightgrey)
    ]))

    elements.append(desc)

    doc.build(elements)
    buffer.seek(0)
    return buffer
