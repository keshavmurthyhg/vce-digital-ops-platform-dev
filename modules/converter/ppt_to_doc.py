import os
import tempfile
from docx import Document

from modules.converter.ppt_extractor import extract_ppt_content
from modules.converter.ppt_slide_renderer import render_ppt_to_images
from modules.converter.ppt_to_doc import add_images_to_doc


def convert_ppt_to_doc(ppt_path, output_docx):
    """
    Final stable flow:
    1. Extract text content
    2. Render slides as images
    3. Insert only valid images into doc
    """

    try:
        doc = Document()

        # -----------------------------
        # Extract textual content
        # -----------------------------
        extracted_text = extract_ppt_content(ppt_path)

        if extracted_text:
            doc.add_heading("PPT Content", level=1)

            for text in extracted_text:
                if text.strip():
                    doc.add_paragraph(text)

        # -----------------------------
        # Render slides to images
        # -----------------------------
        with tempfile.TemporaryDirectory() as temp_dir:
            image_paths = render_ppt_to_images(
                ppt_path,
                temp_dir
            )

            print(f"Generated slide images: {image_paths}")

            valid_images = []

            for img_path in image_paths:
                if (
                    img_path
                    and os.path.exists(img_path)
                    and os.path.getsize(img_path) > 0
                ):
                    valid_images.append(img_path)

            print(f"Valid images count: {len(valid_images)}")

            # -----------------------------
            # Add images only if valid
            # -----------------------------
            if valid_images:
                doc.add_page_break()
                doc.add_heading("PPT Slides", level=1)

                add_images_to_doc(
                    doc,
                    valid_images
                )
            else:
                print("No valid PPT images found")

        doc.save(output_docx)
        return output_docx

    except Exception as e:
        print(f"PPT conversion failed: {e}")
        raise
