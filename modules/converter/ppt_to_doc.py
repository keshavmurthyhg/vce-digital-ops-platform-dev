from pptx import Presentation
from docx import Document
from docx.shared import Inches
import os

def ppt_to_word(ppt_path, output_docx):
    prs = Presentation(ppt_path)
    doc = Document()

    for i, slide in enumerate(prs.slides):
        doc.add_heading(f"Slide {i+1}", level=1)

        for shape in slide.shapes:
            if hasattr(shape, "text"):
                doc.add_paragraph(shape.text)

            # Extract images
            if shape.shape_type == 13:  # Picture
                image = shape.image
                image_bytes = image.blob
                image_path = f"temp_image_{i}.png"

                with open(image_path, "wb") as f:
                    f.write(image_bytes)

                doc.add_picture(image_path, width=Inches(5))
                os.remove(image_path)

        doc.add_page_break()

    doc.save(output_docx)
