import os
from docx import Document
from docx.shared import Inches

from modules.converter.ppt_extractor import extract_ppt_content
from modules.converter.ppt_slide_renderer import render_ppt_slides_to_images
from modules.converter.ppt_extractor import convert_ppt_to_images


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
        # Render slides
        # -----------------------------------
        rendered_output = render_ppt_slides_to_images(ppt_path)

        print(f"Renderer output: {rendered_output}")

        # Case 1 → renderer returned cleaned PPT path
        if isinstance(rendered_output, str):
            print("Renderer returned PPT path. Converting to images...")
            image_paths = convert_ppt_to_images(rendered_output)

        # Case 2 → renderer already returned image list
        elif isinstance(rendered_output, list):
            image_paths = rendered_output

        else:
            image_paths = []

        print(f"Final image paths: {image_paths}")

        # -----------------------------------
        # Validate images
        # -----------------------------------
        valid_images = []

        for img_path in image_paths:
            try:
                if (
                    img_path
                    and os.path.exists(img_path)
                    and os.path.getsize(img_path) > 0
                ):
                    valid_images.append(img_path)

            except Exception as e:
                print(f"Skipping invalid image {img_path}: {e}")

        print(f"Valid images count: {len(valid_images)}")

        # -----------------------------------
        # Add slides to doc
        # -----------------------------------
        if valid_images:
            doc.add_page_break()
            doc.add_heading("PPT Slides", level=1)

            add_images_to_doc(
                doc,
                valid_images
            )
        else:
            doc.add_paragraph(
                "No valid PPT slide images found."
            )

        # -----------------------------------
        # Save document
        # -----------------------------------
        doc.save(output_docx)

        return output_docx

    except Exception as e:
        print(f"PPT conversion failed: {e}")
        raise


# backward compatibility
def ppt_to_word(ppt_path, output_docx):
    return convert_ppt_to_doc(
        ppt_path,
        output_docx
    )
