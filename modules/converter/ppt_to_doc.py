import os

from docx import Document
from docx.shared import Inches

from modules.converter.ppt_metadata import extract_slide1_metadata
from modules.converter.ppt_slide_renderer import render_ppt_slides_to_images


def add_header_table(doc, metadata):
    """
    Add metadata table extracted from slide 1
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

    # Incident
    table.cell(0, 0).text = "Incident"
    table.cell(0, 1).text = metadata.get(
        "incident",
        "-"
    )

    # Created Date
    table.cell(1, 0).text = "Created Date"
    table.cell(1, 1).text = metadata.get(
        "created_date",
        "-"
    )


def add_slide_images(doc, slide_images):
    """
    Add rendered PPT slides as images
    Skip slide 1 because metadata is already extracted from it
    """

    if not slide_images:
        doc.add_paragraph(
            "No PPT slides found."
        )
        return

    # Add section title once
    doc.add_page_break()
    doc.add_heading(
        "PPT Screenshots",
        level=1
    )

    # Skip first slide
    for img_path in slide_images[1:]:
        if os.path.exists(img_path):
            doc.add_picture(
                img_path,
                width=Inches(6.5)
            )
            doc.add_paragraph("")


def ppt_to_word(ppt_path, output_docx):
    """
    Convert PPT to Word:
    1. Extract metadata from slide 1
    2. Render all slides as images
    3. Insert slides into Word
    """

    # Extract metadata from first slide
    metadata = extract_slide1_metadata(
        ppt_path
    )

    # Render slides as images
    slide_images = render_ppt_slides_to_images(
        ppt_path
    )

    # Create Word document
    doc = Document()

    # Add metadata section
    add_header_table(
        doc,
        metadata
    )

    # Add slide screenshots
    add_slide_images(
        doc,
        slide_images
    )

    # Save final document
    doc.save(output_docx)

    return output_docx
