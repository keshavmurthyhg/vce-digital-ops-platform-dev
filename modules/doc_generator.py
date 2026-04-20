from docx import Document
from docx.shared import Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from io import BytesIO
import re

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


# ================= CLEAN =================
def clean_text(text):
    if not text:
        return ""
    return re.sub(r"How does the user want.*?\d+", "", str(text), flags=re.I).strip()


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
    text_elem = OxmlElement("w:t")
    text_elem.text = text

    run.append(text_elem)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


# ================= WORD =================
def generate_word_doc(data, root, l2, res, images=None):

    doc = Document()

    # TITLE
    title = doc.add_heading("INCIDENT REPORT", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].bold = True
    title.runs[0].font.color.rgb = RGBColor(31, 78, 121)

    # TABLE
    table = doc.add_table(rows=4, cols=4)
    table.style = "Table Grid"

    def fill(r, c, key, val):
        h = table.rows[r].cells[c]
        v = table.rows[r].cells[c+1]

        h.text = key.upper()

        # grey fill
        shade = OxmlElement("w:shd")
        shade.set(qn("w:fill"), "D9D9D9")
        h._element.get_or_add_tcPr().append(shade)

        for run in h.paragraphs[0].runs:
            run.bold = True

        p = v.paragraphs[0]

        if key == "Incident":
            add_hyperlink(p,
                f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={val}",
                str(val))
        elif key == "Azure Bug":
            add_hyperlink(p,
                f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{val}",
                str(val))
        elif key == "PTC Case":
            add_hyperlink(p,
                f"https://support.ptc.com/app/caseviewer/?case={val}",
                str(val))
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

    t2.rows[0].cells[0].text = "SHORT DESCRIPTION"
    t2.rows[0].cells[1].text = "DESCRIPTION"

    t2.rows[1].cells[0].text = clean_text(data.get("short_description"))
    t2.rows[1].cells[1].text = clean_text(data.get("description"))

    # TEXT
    doc.add_heading("ROOT CAUSE", 1)
    doc.add_paragraph(root)

    if images and images.get("root"):
        doc.add_picture(images["root"], width=Inches(5))

    doc.add_heading("L2 ANALYSIS", 1)
    doc.add_paragraph(l2)

    if images and images.get("l2"):
        doc.add_picture(images["l2"], width=Inches(5))

    doc.add_heading("RESOLUTION", 1)
    doc.add_paragraph(res)

    if images and images.get("res"):
        doc.add_picture(images["res"], width=Inches(5))

    # FOOTER
    section = doc.sections[0]
    footer = section.footer.paragraphs[0]
    footer.text = f"{data.get('number')}    Page    {data.get('priority')}"

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer


# ================= PDF =================
def generate_pdf(data, root, l2, res, images=None):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, leftMargin=40, rightMargin=40)

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>INCIDENT REPORT</b>", styles["Title"]))
    elements.append(Spacer(1,10))

    def link(url, text):
        return Paragraph(f'<link href="{url}">{text}</link>', styles["Normal"])

    def wrap(x):
        return Paragraph(str(x), styles["Normal"])

    table = Table([
        ["INCIDENT", link(f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={data.get('number')}", data.get("number")),
         "CREATED BY", wrap(data.get("created_by"))],

        ["AZURE BUG", link(f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{data.get('azure_bug')}", data.get("azure_bug")),
         "CREATED DATE", wrap(data.get("created_date"))],

        ["PTC CASE", link(f"https://support.ptc.com/app/caseviewer/?case={data.get('ptc_case')}", data.get("ptc_case")),
         "ASSIGNED TO", wrap(data.get("assigned_to"))],

        ["PRIORITY", wrap(data.get("priority")),
         "RESOLVED DATE", wrap(data.get("resolved_date"))]
    ], colWidths=[100,170,100,170])

    table.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('BACKGROUND',(0,0),(0,-1),colors.lightgrey),
        ('BACKGROUND',(2,0),(2,-1),colors.lightgrey),
    ]))

    elements.append(table)

    elements.append(Spacer(1,10))
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

    if images and images.get("root"):
        elements.append(Image(images["root"], width=400, height=200))

    elements.append(Paragraph("<b>L2 ANALYSIS</b>", styles["Heading2"]))
    elements.append(Paragraph(l2, styles["Normal"]))

    if images and images.get("l2"):
        elements.append(Image(images["l2"], width=400, height=200))

    elements.append(Paragraph("<b>RESOLUTION</b>", styles["Heading2"]))
    elements.append(Paragraph(res, styles["Normal"]))

    if images and images.get("res"):
        elements.append(Image(images["res"], width=400, height=200))

    def footer(canvas, doc):
        canvas.drawString(40, 20, data.get("number"))
        canvas.drawCentredString(300, 20, f"Page {doc.page}")
        canvas.drawRightString(550, 20, data.get("priority"))

    doc.build(elements, onFirstPage=footer, onLaterPages=footer)

    buffer.seek(0)
    return buffer
