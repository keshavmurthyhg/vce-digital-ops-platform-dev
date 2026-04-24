from pptx import Presentation
from docx import Document
from docx.shared import Inches
import os
import uuid


def clean_text(text):
    if not text:
        return ""
    try:
        text = text.encode("utf-8", "ignore").decode("utf-8")
    except Exception:
        text = str(text)
    return "".join(ch for ch in text if ch.isprintable())


import re

import re

def extract_slide1_content(slide):
    texts = []

    shapes = sorted(slide.shapes, key=lambda s: getattr(s, "top", 0))

    for shape in shapes:
        if hasattr(shape, "text"):
            txt = clean_text(shape.text.strip())
            if txt:
                texts.append(txt)

    incident = ""
    description = []
    date = ""

    for txt in texts:

        # 🔹 Extract incident even if merged with text
        inc_match = re.search(r"(INC\d+)", txt, re.IGNORECASE)
        if inc_match:
            incident = inc_match.group(1)

            # Remove incident from text → remaining is description
            remaining = txt.replace(incident, "").strip()
            if remaining:
                description.append(remaining)
            continue

        # 🔹 Detect date
        if re.search(r"\d{1,2}-[A-Za-z]{3}-\d{4}", txt):
            date = txt.strip()
            continue

        # 🔹 Everything else
        description.append(txt.strip())

    description_text = " ".join(description) if description else "N/A"

    return incident or "N/A", description_text, date or ""

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def set_cell_bg(cell, color="D9E1F2"):
    """Set background color for table cell"""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), color)
    tcPr.append(shd)


from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


# 🔹 Background color helper
def set_cell_bg(cell, color="D9E1F2"):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), color)
    tcPr.append(shd)


# 🔹 Horizontal line (proper, not text)
def add_horizontal_line(doc):
    p = doc.add_paragraph()
    p_format = p.paragraph_format

    p_pr = p._element.get_or_add_pPr()
    border = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), 'auto')
    border.append(bottom)
    p_pr.append(border)


from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


# 🔹 Background color helper
def set_cell_bg(cell, color="D9E1F2"):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), color)
    tcPr.append(shd)


# 🔹 Horizontal line (proper, not text)
def add_horizontal_line(doc):
    p = doc.add_paragraph()
    p_format = p.paragraph_format

    p_pr = p._element.get_or_add_pPr()
    border = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), 'auto')
    border.append(bottom)
    p_pr.append(border)


from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def set_cell_bg(cell):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), "D9D9D9")
    tcPr.append(shd)


def add_header_table(doc, incident, description, date):

    # 🔹 TITLE (same as report module)
    doc.add_heading("INCIDENT REPORT", 0).alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 🔹 HEADER TABLE (same 4x4 structure)
    table = doc.add_table(rows=4, cols=4)
    table.style = "Table Grid"

    def fill(r, c, key, val):
        h = table.rows[r].cells[c]
        v = table.rows[r].cells[c + 1]

        # Header cell
        p = h.paragraphs[0]
        p.text = key.upper()
        for run in p.runs:
            run.bold = True
        set_cell_bg(h)

        # Value cell
        v.paragraphs[0].text = str(val or "")

    fill(0, 0, "Incident", incident)
    fill(0, 2, "Created By", "PPT Import")

    fill(1, 0, "Azure Bug", "")
    fill(1, 2, "Created Date", date)

    fill(2, 0, "PTC Case", "")
    fill(2, 2, "Assigned To", "")

    fill(3, 0, "Priority", "")
    fill(3, 2, "Resolved Date", "")

    doc.add_paragraph("")

    # 🔹 DESCRIPTION TABLE (exact same structure)
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

    # Split description
    short_desc = description.split("\n")[0] if description else ""

    t2.rows[1].cells[0].text = short_desc
    t2.rows[1].cells[1].text = description

    doc.add_paragraph("")

def ppt_to_word(ppt_path, output_docx):
    prs = Presentation(ppt_path)
    doc = Document()

    # 🔹 Handle Slide 1 separately
    if len(prs.slides) > 0:
        slide1 = prs.slides[0]
        incident, description, date = extract_slide1_content(slide1)

        add_header_table(doc, incident, description, date)
        doc.add_page_break()

    # 🔹 Process remaining slides
    for i, slide in enumerate(prs.slides):

        # Skip slide 1 (already handled)
        if i == 0:
            continue

        doc.add_heading(f"Slide {i+1}", level=1)

        try:
            shapes = sorted(slide.shapes, key=lambda s: getattr(s, "top", 0))
        except Exception:
            shapes = slide.shapes

        has_content = False

        for shape in shapes:

            # TEXT
            if hasattr(shape, "text"):
                raw_text = shape.text.strip()
                if raw_text:
                    cleaned = clean_text(raw_text)
                    if cleaned:
                        doc.add_paragraph(cleaned)
                        has_content = True

            # IMAGE
            try:
                if shape.shape_type == 13:
                    image = shape.image
                    image_bytes = image.blob

                    image_path = f"temp_{uuid.uuid4().hex}.png"

                    with open(image_path, "wb") as f:
                        f.write(image_bytes)

                    doc.add_picture(image_path, width=Inches(5))
                    os.remove(image_path)

                    has_content = True

            except Exception:
                continue

        if not has_content:
            doc.add_paragraph("(No visible content)")

        doc.add_page_break()

    doc.save(output_docx)
