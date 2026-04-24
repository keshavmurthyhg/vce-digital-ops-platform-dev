from pptx import Presentation
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import os
import uuid
import re


# ---------------- HYPERLINK ---------------- #
def add_hyperlink(paragraph, url, text):
    part = paragraph.part
    r_id = part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )

    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)

    run = OxmlElement("w:r")
    text_elem = OxmlElement("w:t")
    text_elem.text = str(text)
    run.append(text_elem)
    hyperlink.append(run)

    paragraph._p.append(hyperlink)


# ---------------- AZURE ---------------- #
def extract_azure_bug(text):
    if not text:
        return ""
    match = re.search(r"\b(\d{5,})\b", text)
    return match.group(1) if match else ""


# ---------------- CLEAN ---------------- #
def clean_text(text):
    if not text:
        return ""
    try:
        text = text.encode("utf-8", "ignore").decode("utf-8")
    except:
        text = str(text)
    return "".join(ch for ch in text if ch.isprintable())


# ---------------- SLIDE 1 ---------------- #
def extract_slide1_content(slide):
    texts = []

    shapes = sorted(slide.shapes, key=lambda s: getattr(s, "top", 0))

    for shape in shapes:
        if hasattr(shape, "text"):
            txt = clean_text(shape.text.strip())
            if txt:
                texts.append(txt)

    incident, description, date = "", [], ""

    for txt in texts:

        inc_match = re.search(r"(INC\d+)", txt, re.IGNORECASE)
        if inc_match:
            incident = inc_match.group(1)
            remaining = txt.replace(incident, "").strip()
            if remaining:
                description.append(remaining)
            continue

        if re.search(r"\d{1,2}-[A-Za-z]{3}-\d{4}", txt):
            date = txt
            continue

        description.append(txt)

    azure = extract_azure_bug(" ".join(texts))

    return incident or "N/A", " ".join(description) or "N/A", date or "", azure


# ---------------- STYLE ---------------- #
def set_cell_bg(cell):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), "D9D9D9")
    tcPr.append(shd)


# ---------------- HEADER ---------------- #
def add_header_table(doc, incident, description, date, azure):

    doc.add_heading("INCIDENT REPORT", 0).alignment = WD_ALIGN_PARAGRAPH.CENTER

    table = doc.add_table(rows=4, cols=4)
    table.style = "Table Grid"

    def fill(r, c, key, val):
        h = table.rows[r].cells[c]
        v = table.rows[r].cells[c + 1]

        p = h.paragraphs[0]
        p.text = key.upper()
        for run in p.runs:
            run.bold = True
        set_cell_bg(h)

        p = v.paragraphs[0]

        if key.lower() == "incident" and val:
            url = f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={val}"
            add_hyperlink(p, url, val)

        elif key.lower() == "azure bug" and val:
            url = f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{val}"
            add_hyperlink(p, url, val)

        else:
            p.text = str(val or "")

    fill(0, 0, "Incident", incident)
    fill(0, 2, "Created By", "PPT Import")

    fill(1, 0, "Azure Bug", azure)
    fill(1, 2, "Created Date", date)

    fill(2, 0, "PTC Case", "")
    fill(2, 2, "Assigned To", "")

    fill(3, 0, "Priority", "")
    fill(3, 2, "Resolved Date", "")

    doc.add_paragraph("")

    t2 = doc.add_table(rows=2, cols=2)
    t2.style = "Table Grid"

    headers = ["SHORT DESCRIPTION", "DESCRIPTION"]

    for i, text in enumerate(headers):
        cell = t2.rows[0].cells[i]
        p = cell.paragraphs[0]
        p.text = text
        for run in p.runs:
            run.bold = True
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_bg(cell)

    short_desc = description.split("\n")[0] if description else ""
    t2.rows[1].cells[0].text = short_desc
    t2.rows[1].cells[1].text = description

    doc.add_paragraph("")


# ---------------- FOOTER ---------------- #
def add_footer(doc, incident):
    section = doc.sections[0]
    footer = section.footer.paragraphs[0]
    footer.clear()

    tab_stops = footer.paragraph_format.tab_stops
    tab_stops.add_tab_stop(Inches(3.25), WD_TAB_ALIGNMENT.CENTER)
    tab_stops.add_tab_stop(Inches(6.5), WD_TAB_ALIGNMENT.RIGHT)

    run = footer.add_run(f"{incident}\tPage ")

    fld1 = OxmlElement('w:fldChar')
    fld1.set(qn('w:fldCharType'), 'begin')

    instr = OxmlElement('w:instrText')
    instr.text = "PAGE"

    fld2 = OxmlElement('w:fldChar')
    fld2.set(qn('w:fldCharType'), 'end')

    run._r.append(fld1)
    run._r.append(instr)
    run._r.append(fld2)

    footer.add_run("\tPPT")


# ---------------- MAIN ---------------- #
def ppt_to_word(ppt_path, output_docx):
    prs = Presentation(ppt_path)
    doc = Document()

    if prs.slides:
        incident, description, date, azure = extract_slide1_content(prs.slides[0])
        add_header_table(doc, incident, description, date, azure)
        add_footer(doc, incident)

    for i, slide in enumerate(prs.slides):
        if i == 0:
            continue

        doc.add_heading(f"Slide {i+1}", level=1)

        shapes = sorted(slide.shapes, key=lambda s: getattr(s, "top", 0))

        for shape in shapes:
            if hasattr(shape, "text") and shape.text.strip():
                doc.add_paragraph(clean_text(shape.text))

            if shape.shape_type == 13:
                img_path = f"temp_{uuid.uuid4().hex}.png"
                with open(img_path, "wb") as f:
                    f.write(shape.image.blob)
                doc.add_picture(img_path, width=Inches(5))
                os.remove(img_path)

        doc.add_page_break()

    doc.save(output_docx)
