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


# ================= CLEAN =================
def clean_text(text):
    if not text:
        return ""
    return re.sub(
        r"How does the user want.*?\d+",
        "",
        str(text),
        flags=re.IGNORECASE
    ).strip()


# ================= WORD HYPERLINK =================
def add_hyperlink(paragraph, url, text):
    part = paragraph.part
    r_id = part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)

    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)

    run = OxmlElement("w:r")
    text_elem = OxmlElement("w:t")
    text_elem.text = text
    run.append(text_elem)

    hyperlink.append(run)
    paragraph._p.append(hyperlink)


# ================= WORD =================
def generate_word_doc(data, root, l2, res):

    doc = Document()

    # TITLE
    title = doc.add_heading("INCIDENT REPORT", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # ===== TABLE 1 =====
    table = doc.add_table(rows=4, cols=4)
    table.style = "Table Grid"

    def fill(r, c, key, value):
        cell1 = table.rows[r].cells[c]
        cell2 = table.rows[r].cells[c+1]

        cell1.text = key.upper()
        cell2.text = ""

        p = cell2.paragraphs[0]

        if key == "Incident":
            add_hyperlink(p,
                f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={value}",
                str(value))
        elif key == "Azure Bug":
            add_hyperlink(p,
                f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{value}",
                str(value))
        elif key == "PTC Case":
            add_hyperlink(p,
                f"https://support.ptc.com/app/caseviewer/?case={value}",
                str(value))
        else:
            p.text = str(value)

        # grey header
        shading = OxmlElement("w:shd")
        shading.set(qn("w:fill"), "D9D9D9")
        cell1._element.get_or_add_tcPr().append(shading)

    fill(0,0,"Incident",data["number"])
    fill(0,2,"Created By",data["created_by"])
    fill(1,0,"Azure Bug",data["azure_bug"])
    fill(1,2,"Created Date",data["created_date"])
    fill(2,0,"PTC Case",data["ptc_case"])
    fill(2,2,"Assigned To",data["assigned_to"])
    fill(3,0,"Priority",data["priority"])
    fill(3,2,"Resolved Date",data["resolved_date"])

    doc.add_paragraph("")

    # ===== TABLE 2 =====
    desc = doc.add_table(rows=2, cols=2)
    desc.style = "Table Grid"

    headers = ["SHORT DESCRIPTION", "DESCRIPTION"]

    for i in range(2):
        cell = desc.rows[0].cells[i]
        cell.text = headers[i]
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

        shading = OxmlElement("w:shd")
        shading.set(qn("w:fill"), "D9D9D9")
        cell._element.get_or_add_tcPr().append(shading)

    desc.rows[1].cells[0].text = clean_text(data["short_description"])
    desc.rows[1].cells[1].text = clean_text(data["description"])

    # TEXT
    doc.add_heading("ROOT CAUSE", 1)
    doc.add_paragraph(root)

    doc.add_heading("L2 ANALYSIS", 1)
    doc.add_paragraph(l2)

    doc.add_heading("RESOLUTION", 1)
    doc.add_paragraph(res)

    # FOOTER
    section = doc.sections[0]
    footer = section.footer.paragraphs[0]
    footer.text = f"{data['number']}        Page        {data['priority']}"

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

    elements.append(Paragraph("<b>INCIDENT REPORT</b>", styles["Title"]))
    elements.append(Spacer(1,10))

    def link(url,text):
        return Paragraph(f'<link href="{url}">{text}</link>', styles["Normal"])

    table_data = [
        ["INCIDENT", link(f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={data['number']}", data["number"]),
         "CREATED BY", data["created_by"]],

        ["AZURE BUG", link(f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{data['azure_bug']}", data["azure_bug"]),
         "CREATED DATE", data["created_date"]],

        ["PTC CASE", link(f"https://support.ptc.com/app/caseviewer/?case={data['ptc_case']}", data["ptc_case"]),
         "ASSIGNED TO", data["assigned_to"]],

        ["PRIORITY", data["priority"],
         "RESOLVED DATE", data["resolved_date"]]
    ]

    table = Table(table_data, colWidths=[100,200,100,200])

    table.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('BACKGROUND',(0,0),(0,-1),colors.lightgrey),
        ('BACKGROUND',(2,0),(2,-1),colors.lightgrey),
        ('VALIGN',(0,0),(-1,-1),'TOP')
    ]))

    elements.append(table)
    elements.append(Spacer(1,10))

    desc = Table([
        ["SHORT DESCRIPTION","DESCRIPTION"],
        [clean_text(data["short_description"]), clean_text(data["description"])]
    ], colWidths=[220,280])

    desc.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
        ('VALIGN',(0,0),(-1,-1),'TOP')
    ]))

    elements.append(desc)

    elements.append(Spacer(1,10))
    elements.append(Paragraph("<b>ROOT CAUSE</b>", styles["Heading2"]))
    elements.append(Paragraph(root, styles["Normal"]))

    elements.append(Paragraph("<b>L2 ANALYSIS</b>", styles["Heading2"]))
    elements.append(Paragraph(l2, styles["Normal"]))

    elements.append(Paragraph("<b>RESOLUTION</b>", styles["Heading2"]))
    elements.append(Paragraph(res, styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer
