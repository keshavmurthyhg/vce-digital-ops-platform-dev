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


def add_header_table(doc, incident, description, date):

    # 🔹 TITLE (exact report style)
    title = doc.add_paragraph()
    run = title.add_run("Incident Report")
    run.bold = True
    run.font.size = Pt(26)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph("")  # spacing

    # 🔹 Clean divider line
    add_horizontal_line(doc)

    doc.add_paragraph("")  # spacing

    # 🔹 TABLE
    table = doc.add_table(rows=3, cols=2)
    table.style = "Table Grid"
    table.autofit = False

    # 🔹 Fixed widths (important for alignment)
    table.columns[0].width = Inches(2.5)
    table.columns[1].width = Inches(4.5)

    labels = ["Incident Number", "Description", "Date"]
    values = [incident, description, date]

    for i in range(3):
        # Left cell (label)
        left_cell = table.cell(i, 0)
        left_para = left_cell.paragraphs[0]
        left_run = left_para.add_run(labels[i])
        left_run.bold = True
        left_run.font.size = Pt(11)

        set_cell_bg(left_cell, "D9E1F2")

        # Right cell (value)
        right_cell = table.cell(i, 1)
        right_para = right_cell.paragraphs[0]
        right_run = right_para.add_run(values[i])
        right_run.font.size = Pt(11)

    doc.add_paragraph("")  # spacing after table

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
