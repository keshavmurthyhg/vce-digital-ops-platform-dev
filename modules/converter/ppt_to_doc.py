import os
import fitz
import tempfile

from docx import Document
from docx.shared import Inches

from modules.converter.ppt_slide_renderer import render_ppt_slides_to_images
from modules.converter.ppt_metadata import extract_slide1_metadata


def pdf_to_images(pdf_path):
    temp_dir = tempfile.mkdtemp()
    image_paths = []

    pdf = fitz.open(pdf_path)

    for i, page in enumerate(pdf):
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_path = os.path.join(temp_dir, f"slide_{i+1}.png")
        pix.save(img_path)
        image_paths.append(img_path)

    return image_paths


def add_header_table(doc, metadata):
    doc.add_heading("INCIDENT REPORT", 0)

    table = doc.add_table(rows=2, cols=2)
    table.style = "Table Grid"

    table.cell(0, 0).text = "Incident"
    table.cell(0, 1).text = metadata["incident"]

    table.cell(1, 0).text = "Created Date"
    table.cell(1, 1).text = metadata["created_date"]


def ppt_to_word(ppt_path, output_docx):
    metadata = extract_slide1_metadata(ppt_path)

    pdf_path = render_ppt_slides_to_images(ppt_path)
    images = pdf_to_images(pdf_path)

    doc = Document()

    add_header_table(doc, metadata)

    for img in images[1:]:  # skip slide1
        doc.add_page_break()
        doc.add_picture(img, width=Inches(6.8))

    doc.save(output_docx)

    return output_docx
