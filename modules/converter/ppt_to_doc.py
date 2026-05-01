import os

from docx import Document
from docx.shared import Inches

from modules.converter.ppt_metadata import extract_slide1_metadata
from modules.converter.ppt_slide_renderer import render_ppt_slides_to_images


def add_header_table(doc, metadata):
    """
    Add metadata table from slide 1
    """
    doc.add_heading(
        "INCIDENT REPORT",
        level=0
    )

    table = doc.add_table(
        rows=2,
        cols=2
    )
    table.style = "Table Grid"

    table.cell(0, 0).text = "Incident"
    table.cell(0, 1).text = metadata.get(
        "incident", "-"
    )

    table.cell(1, 0).text = "Created Date"
    table.cell(1, 1).text = metadata.get(
        "created_date", "-"
    )


def add_slide_images(doc, slide_images):
    """
    Add rendered PPT slides into Word
    """
    if not slide_images:
        doc.add_paragraph(
            "No PPT slides found."
        )
        return

    # Skip slide 1 because metadata already extracted
    for img in slide_images[1:]:
        if os.path.exists(img):
            doc.add_page_break()
            doc.add_picture(
                img,
                width=Inches(6.8)
            )


def ppt_to_word(ppt_path, output_docx):
    """
    Convert PPT to Word:
    - Extract metadata from slide 1
    - Render complete slides as images
    - Add them into Word
    """

    # Extract incident metadata
    metadata = extract_slide1_metadata(
        ppt_path
    )

    # Render full slides as images
    slide_images = render_ppt_slides_to_images(
        ppt_path
    )

    # Create Word document
    doc = Document()

    # Add metadata table
    add_header_table(
        doc,
        metadata
    )

    # Add slide images
    add_slide_images(
        doc,
        slide_images
    )

    # Save final document
    doc.save(output_docx)

    return output_docx
