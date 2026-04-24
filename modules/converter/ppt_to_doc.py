from pptx import Presentation
from docx import Document
from docx.shared import Inches
import os
import uuid


# 🔹 Clean text to avoid XML errors
def clean_text(text):
    if not text:
        return ""

    # Remove problematic characters
    try:
        text = text.encode("utf-8", "ignore").decode("utf-8")
    except Exception:
        text = str(text)

    # Remove control characters
    return "".join(ch for ch in text if ch.isprintable())


def ppt_to_word(ppt_path, output_docx):
    prs = Presentation(ppt_path)
    doc = Document()

    for i, slide in enumerate(prs.slides):
        doc.add_heading(f"Slide {i+1}", level=1)

        # Sort shapes by vertical position (top)
        try:
            shapes = sorted(slide.shapes, key=lambda s: getattr(s, "top", 0))
        except Exception:
            shapes = slide.shapes

        has_content = False

        for shape in shapes:

            # 🔹 TEXT HANDLING
            if hasattr(shape, "text"):
                raw_text = shape.text.strip()

                if raw_text:
                    cleaned = clean_text(raw_text)

                    if cleaned:
                        doc.add_paragraph(cleaned)
                        has_content = True

            # 🔹 IMAGE HANDLING
            try:
                if shape.shape_type == 13:  # Picture
                    image = shape.image
                    image_bytes = image.blob

                    image_path = f"temp_{uuid.uuid4().hex}.png"

                    with open(image_path, "wb") as f:
                        f.write(image_bytes)

                    doc.add_picture(image_path, width=Inches(5))
                    os.remove(image_path)

                    has_content = True

            except Exception:
                # Skip problematic images silently
                continue

        # 🔹 If slide is empty
        if not has_content:
            doc.add_paragraph("(No visible content)")

        doc.add_page_break()

    doc.save(output_docx)
