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

        # 🔹 Incident detection
        if txt.upper().startswith("INC"):
            incident = txt.strip()
            continue

        # 🔹 Date detection (simple pattern)
        if re.search(r"\d{1,2}-[A-Za-z]{3}-\d{4}", txt):
            date = txt.strip()
            continue

        # 🔹 Everything else = description
        description.append(txt.strip())

    description_text = " ".join(description) if description else "N/A"

    return incident or "N/A", description_text, date or ""


def add_header_table(doc, incident, description, date):
    # Title
    doc.add_heading("Incident Report", level=0)

    # Table (2 columns)
    table = doc.add_table(rows=3, cols=2)
    table.style = "Table Grid"

    table.cell(0, 0).text = "Incident Number"
    table.cell(0, 1).text = incident

    table.cell(1, 0).text = "Description"
    table.cell(1, 1).text = description

    table.cell(2, 0).text = "Date"
    table.cell(2, 1).text = date


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
