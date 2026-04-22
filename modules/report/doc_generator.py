from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from io import BytesIO
from datetime import datetime
import re

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

def clean_text(text):
    if not text:
        return ""
    return re.sub(r"How does the user want.*?\d+", "", str(text), flags=re.I).strip()

def format_date(date_str):
    if not date_str:
        return ""
    try:
        return datetime.strptime(str(date_str), "%Y-%m-%d").strftime("%d-%b-%Y")
    except:
        return str(date_str)

# ---------------- WORD ---------------- #

def add_hyperlink(paragraph, url, text):
    part = paragraph.part
    r_id = part.relate_to(url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True)

    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)

    run = OxmlElement("w:r")
    text_elem = OxmlElement("w:t")
    text_elem.text = text
    run.append(text_elem)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


def set_cell_bg(cell):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), "D9D9D9")
    tcPr.append(shd)


def generate_word_doc(data, root, l2, res, images=None):
    doc = Document()

    doc.add_heading("INCIDENT REPORT", 0).alignment = WD_ALIGN_PARAGRAPH.CENTER

    # ---------- HEADER TABLE ----------
    table = doc.add_table(rows=4, cols=4)
    table.style = "Table Grid"

    from docx.enum.table import WD_TABLE_ALIGNMENT
    table.autofit = True
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # ✅ FULL WIDTH FUNCTION
    def set_table_full_width(table):
        tbl = table._element
        tblPr = tbl.xpath("./w:tblPr")[0]

        tblW = OxmlElement('w:tblW')
        tblW.set(qn('w:type'), 'pct')
        tblW.set(qn('w:w'), "5000")

        tblPr.append(tblW)

    set_table_full_width(table)

    # ---------- FILL FUNCTION ----------
    def fill(r, c, key, val):
        h = table.rows[r].cells[c]
        v = table.rows[r].cells[c + 1]

        p = h.paragraphs[0]
        p.text = key.upper()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for run in p.runs:
            run.bold = True
        set_cell_bg(h)

        p = v.paragraphs[0]
        if key == "Incident":
            add_hyperlink(p, f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={val}", str(val))
        elif key == "Azure Bug":
            add_hyperlink(p, f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{val}", str(val))
        elif key == "PTC Case":
            add_hyperlink(p, f"https://support.ptc.com/app/caseviewer/?case={val}", str(val))
        else:
            p.text = str(val or "")

    # ---------- FILL DATA ----------
    fill(0,0,"Incident",data.get("number"))
    fill(0,2,"Created By",data.get("created_by"))
    fill(1,0,"Azure Bug",data.get("azure_bug"))
    fill(1,2,"Created Date", format_date(data.get("created_date")))
    fill(2,0,"PTC Case",data.get("ptc_case"))
    fill(2,2,"Assigned To",data.get("assigned_to"))
    fill(3,0,"Priority",data.get("priority"))
    fill(3,2,"Resolved Date", format_date(data.get("resolved_date")))

    doc.add_paragraph("")

    # ---------- DESCRIPTION TABLE ----------
    t2 = doc.add_table(rows=2, cols=2)
    t2.style = "Table Grid"

    t2.autofit = True
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_full_width(t2)

    headers = ["SHORT DESCRIPTION", "DESCRIPTION"]
    for i, text in enumerate(headers):
        cell = t2.rows[0].cells[i]
        p = cell.paragraphs[0]
        p.text = text
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.bold = True
        set_cell_bg(cell)

    for i, txt in enumerate([
        clean_text(data.get("short_description")),
        clean_text(data.get("description"))
    ]):
        p = t2.rows[1].cells[i].paragraphs[0]
        p.text = txt
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    # ---------- SECTIONS ----------
    for title, content in [("ROOT CAUSE", root), ("L2 ANALYSIS", l2), ("RESOLUTION", res)]:
        h = doc.add_heading(title, 1)
        h.alignment = WD_ALIGN_PARAGRAPH.LEFT

        p = doc.add_paragraph(content or "-")
        p.paragraph_format.space_after = Inches(0.15)

    # ---------- FOOTER ----------
    section = doc.sections[0]
    footer = section.footer.paragraphs[0]
    footer.clear()

    tab_stops = footer.paragraph_format.tab_stops
    tab_stops.add_tab_stop(Inches(3.25), WD_TAB_ALIGNMENT.CENTER)
    tab_stops.add_tab_stop(Inches(6.5), WD_TAB_ALIGNMENT.RIGHT)

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
    buffer.seek(0)
    return buffer.getvalue()

# ---------------- PDF ---------------- #

def generate_pdf(data, root, l2, res, images=None):

    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import letter
    from io import BytesIO

    buffer = BytesIO()
    
    styles = getSampleStyleSheet()

    elements = []

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=50
    )
    
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Table
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    
    title_style = ParagraphStyle(
        name="TitleCenter",
        parent=styles["Title"],
        alignment=1,
        spaceAfter=-6   # 🔥 key line
    )
    
   # Title
    elements.append(Paragraph("<b>INCIDENT REPORT</b>", styles["Title"]))
    
    # 🔥 CONTROL GAP HERE (THIS is what you need)
    elements.append(Spacer(1, -3))   # move line UP
    
    # Line (fixed width for now as you wanted)
    line = Table([[""]], colWidths=[520])
    line.setStyle([
        ("LINEBELOW", (0, 0), (-1, -1), 1, colors.black)
    ])
    
    elements.append(line)
    
    # Gap before table
    elements.append(Spacer(1, 6))
    
    def link(url, text):
        return Paragraph(f'<link href="{url}">{text}</link>', styles["Normal"])

    def wrap(x):
        return Paragraph(str(x or ""), styles["Normal"])

    # HEADER TABLE
    table = Table([
        ["INCIDENT", link(f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={data.get('number')}", data.get('number')),
         "CREATED BY", wrap(data.get('created_by'))],
        ["AZURE BUG", link(f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{data.get('azure_bug')}", data.get('azure_bug')),
         "CREATED DATE", wrap(format_date(data.get('created_date')))],
        ["PTC CASE", link(f"https://support.ptc.com/app/caseviewer/?case={data.get('ptc_case')}", data.get('ptc_case')),
         "ASSIGNED TO", wrap(data.get('assigned_to'))],
        ["PRIORITY", wrap(data.get('priority')),
         "RESOLVED DATE", wrap(format_date(data.get('resolved_date')))]
    ], colWidths=[100,160,100,160])

    table.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('BACKGROUND',(0,0),(0,-1),colors.lightgrey),
        ('BACKGROUND',(2,0),(2,-1),colors.lightgrey),
        ('FONTNAME',(0,0),(0,-1),'Helvetica-Bold'),
        ('FONTNAME',(2,0),(2,-1),'Helvetica-Bold'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ]))

    elements.append(table)
    elements.append(Spacer(1,15))

    # DESCRIPTION
    desc_table = Table([
        ["SHORT DESCRIPTION","DESCRIPTION"],
        [wrap(clean_text(data.get("short_description"))),
         wrap(clean_text(data.get("description")))]
    ], colWidths=[260,260])

    desc_table.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('ALIGN',(0,0),(-1,0),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
    ]))

    elements.append(desc_table)
    elements.append(Spacer(1,20))

    # ✅ ADD MISSING SECTIONS
    def section(title, content):
        elements.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
        elements.append(Spacer(1,6))
        elements.append(Paragraph(content or "-", styles["Normal"]))
        elements.append(Spacer(1,15))

    section("ROOT CAUSE", root)
    section("L2 ANALYSIS", l2)
    section("RESOLUTION", res)

    # FOOTER
    def footer(canvas, doc):
        width, _ = letter
        canvas.setFont('Helvetica',9)
        canvas.drawString(40,20,str(data.get("number")))
        canvas.drawCentredString(width/2,20,f"Page {doc.page}")
        canvas.drawRightString(width-40,20,str(data.get("priority")))
    
    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    pdf_bytes = buffer.getvalue()
   
    # extra safety
    if not pdf_bytes or len(pdf_bytes) < 1000:
        raise ValueError("PDF generation failed or empty")

    buffer.close()
    return pdf_bytes
