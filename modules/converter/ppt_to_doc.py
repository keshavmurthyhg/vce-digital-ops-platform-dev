from pptx import Presentation
from docx import Document
from docx.shared import Inches
import os

def ppt_to_word(ppt_path, output_docx):
    prs = Presentation(ppt_path)
    doc = Document()

    for i, slide in enumerate(prs.slides):
        doc.add_heading(f"Slide {i+1}", level=1)

        # Sort shapes by vertical position (TOP)
        shapes = sorted(slide.shapes, key=lambda s: getattr(s, "top", 0))

        for shape in shapes:

            # TEXT
            if hasattr(shape, "text") and shape.text.strip():
                doc.add_paragraph(shape.text)

            # IMAGE
            if shape.shape_type == 13:
                image = shape.image
                image_bytes = image.blob
                image_path = f"temp_{i}.png"

                with open(image_path, "wb") as f:
                    f.write(image_bytes)

                doc.add_picture(image_path, width=Inches(5))
                os.remove(image_path)

        doc.add_page_break()

    doc.save(output_docx)
