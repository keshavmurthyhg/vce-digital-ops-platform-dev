from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from io import BytesIO
import re

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter


def clean_text(text):
    if not text:
        return ""
    return re.sub(r"How does the user want.*?\d+", "", str(text), flags=re.I).strip()


# ---------- WORD ---------- #

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

    # blue color
    rPr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "0000FF")
    rPr.append(color)
    run.append(rPr)

    t = OxmlElement("w:t")
    t.text = str(text)
    run.append(t)

    hyperlink.append(run)
    paragraph._p.append(hyperlink)


def set_cell_bg(cell):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), "D9D9D9")
    tcPr.append(shd)


def generate_word_doc(data, root, l2, res, images=None):

    doc = Document()

    # TITLE
    doc.add_heading("INCIDENT REPORT", 0).alignment = WD_ALIGN_PARAGRAPH.CENTER

    # MAIN TABLE
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

        p = h.paragraphs[0]
        p.text = key.upper()
        for run in p.runs:
            run.bold = True
        set_cell_bg(h)

        p = v.paragraphs[0]

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
            p.text = str(val)

    fill(0,0,"Incident",data.get("number"))
    fill(0,2,"Created By",data.get("created_by"))
    fill(1,0,"Azure Bug",data.get("azure_bug"))
    fill(1,2,"Created Date",data.get("created_date"))
    fill(2,0,"PTC Case",data.get("ptc_case"))
    fill(2,2,"Assigned To",data.get("assigned_to"))
    fill(3,0,"Priority",data.get("priority"))
    fill(3,2,"Resolved Date",data.get("resolved_date"))

    doc.add_paragraph("")

    # DESCRIPTION TABLE
    t2 = doc.add_table(rows=2, cols=2)
    t2.style = "Table Grid"

    headers = ["SHORT DESCRIPTION", "DESCRIPTION"]
    for i, text in enumerate(headers):
        cell = t2.rows[0].cells[i]
        p = cell.paragraphs[0]
        p.text = text
        for run in p.runs:
            run.bold = True
        set_cell_bg(cell)

    t2.rows[1].cells[0].text = clean_text(data.get("short_description"))
    t2.rows[1].cells[1].text = clean_text(data.get("description"))

    # SECTIONS + IMAGES
    sections = [
        ("ROOT CAUSE", root, "root"),
        ("L2 ANALYSIS", l2, "l2"),
        ("RESOLUTION", res, "res"),
    ]

    for title, content, key in sections:
        doc.add_heading(title, 1)
        doc.add_paragraph(content or "")

        if images and images.get(key):
            doc.add_picture(images[key], width=Inches(4.5))

    # FOOTER
    section = doc.sections[0]
    footer = section.footer.paragraphs[0]
    footer.clear()

    tab_stops = footer.paragraph_format.tab_stops
    tab_stops.add_tab_stop(Inches(3.2), WD_TAB_ALIGNMENT.CENTER)
    tab_stops.add_tab_stop(Inches(6.0), WD_TAB_ALIGNMENT.RIGHT)

    run = footer.add_run(f"{data.get('number')}\tPage ")

    fld1 = OxmlElement('w:fldChar')
    fld1.set(qn('w:fldCharType'), 'begin')

    instr = OxmlElement('w:instrText')
    instr.text = "PAGE"

    fld2 = OxmlElement('w:fldChar')
    fld2.set(qn('w:fldCharType'), 'end')

    run._r.append(fld1)
    run._r.append(instr)
    run._r.append(fld2)

    footer.add_run(f"\t{data.get('priority')}")

    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


# ---------- PDF ---------- #

def generate_pdf(data, root, l2, res, images=None):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>INCIDENT REPORT</b>", styles["Title"]))
    elements.append(Spacer(1,10))

    def link(url, text):
        return Paragraph(f'<link href="{url}">{text}</link>', styles["Normal"])

    def wrap(x):
        return Paragraph(str(x), styles["Normal"])

    table = Table([
        ["INCIDENT", link(f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={data.get('number')}", data.get('number')),
         "CREATED BY", wrap(data.get('created_by'))],
        ["AZURE BUG", link(f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{data.get('azure_bug')}", data.get('azure_bug')),
         "CREATED DATE", wrap(data.get('created_date'))],
        ["PTC CASE", link(f"https://support.ptc.com/app/caseviewer/?case={data.get('ptc_case')}", data.get('ptc_case')),
         "ASSIGNED TO", wrap(data.get('assigned_to'))],
        ["PRIORITY", wrap(data.get('priority')),
         "RESOLVED DATE", wrap(data.get('resolved_date'))]
    ], colWidths=[100,170,100,170])

    table.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('BACKGROUND',(0,0),(0,-1),colors.lightgrey),
        ('BACKGROUND',(2,0),(2,-1),colors.lightgrey),
        ('FONTNAME',(0,0),(0,-1),'Helvetica-Bold'),
        ('FONTNAME',(2,0),(2,-1),'Helvetica-Bold'),
    ]))

    elements.append(table)
    elements.append(Spacer(1,15))

    desc_table = Table([
        ["SHORT DESCRIPTION","DESCRIPTION"],
        [wrap(clean_text(data.get("short_description"))), wrap(clean_text(data.get("description")))]
    ])

    desc_table.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
    ]))

    elements.append(desc_table)
    elements.append(Spacer(1,15))

    # SECTIONS
    for title, content in [("ROOT CAUSE", root), ("L2 ANALYSIS", l2), ("RESOLUTION", res)]:
        elements.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
        elements.append(Paragraph(content or "", styles["Normal"]))
        elements.append(Spacer(1,10))

    def footer(canvas, doc):
        width, _ = letter
        canvas.setFont('Helvetica',9)
        canvas.drawString(40,20,str(data.get("number")))
        canvas.drawCentredString(width/2,20,f"Page {doc.page}")
        canvas.drawRightString(width-40,20,str(data.get("priority")))

    doc.build(elements, onFirstPage=footer, onLaterPages=footer)

    return buffer.getvalue()
