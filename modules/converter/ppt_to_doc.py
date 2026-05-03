import os
import tempfile
from docx import Document
from docx.shared import Inches

from modules.converter.ppt_extractor import extract_ppt_content
from modules.converter.ppt_slide_renderer import render_ppt_slides_to_images


def add_images_to_doc(doc, image_paths):
    """
    Add slide images into Word document
    """

    for img_path in image_paths:
        try:
            if os.path.exists(img_path) and os.path.getsize(img_path) > 0:
                doc.add_picture(
                    img_path,
                    width=Inches(6.5)
                )
                doc.add_page_break()

        except Exception as e:
            print(f"Failed to insert image {img_path}: {e}")


def convert_ppt_to_doc(ppt_path, output_docx):
    """
    Convert PPT -> Word
    """

    try:
        doc = Document()

        # -----------------------------------
        # Extract text content
        # -----------------------------------
        extracted_text = extract_ppt_content(ppt_path)

        if extracted_text:
            doc.add_heading("PPT Content", level=1)

            for text in extracted_text:
                if text and text.strip():
                    doc.add_paragraph(text)

        # -----------------------------------
        # Convert slides to images
        # -----------------------------------
        image_paths = render_ppt_slides_to_images(
            ppt_path
        )

        print(f"Generated images: {image_paths}")

        valid_images = []

        for img_path in image_paths:
            if (
                img_path
                and os.path.exists(img_path)
                and os.path.getsize(img_path) > 0
            ):
                valid_images.append(img_path)

        print(f"Valid images count: {len(valid_images)}")

        if valid_images:
            doc.add_page_break()
            doc.add_heading("PPT Slides", level=1)

            add_images_to_doc(
                doc,
                valid_images
            )
        else:
            print("No valid slide images found")

        # -----------------------------------
        # Save final document
        # -----------------------------------
        doc.save(output_docx)

        return output_docx

    except Exception as e:
        print(f"PPT conversion failed: {e}")
        raise


# backward compatibility for converter.py
def ppt_to_word(ppt_path, output_docx):
    return convert_ppt_to_doc(
        ppt_path,
        output_docx
    )
