import os
import tempfile
import uuid
import subprocess

from pdf2image import convert_from_path
from PIL import Image
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE


def is_title_slide(img_path):
    """
    Detect title slides:
    mostly white background + very little actual content
    """
    img = Image.open(img_path).convert("RGB")
    width, height = img.size

    center = img.crop((
        width * 0.2,
        height * 0.2,
        width * 0.8,
        height * 0.8
    ))

    gray = center.convert("L")
    histogram = gray.histogram()

    white_pixels = histogram[255]
    total_pixels = sum(histogram)

    white_ratio = white_pixels / total_pixels

    return white_ratio > 0.85


def remove_ppt_background(input_ppt):
    """
    Remove large decorative PPT theme/background shapes
    while preserving:
    - screenshots
    - arrows
    - annotations
    - textboxes
    """

    prs = Presentation(input_ppt)

    slide_width = prs.slide_width
    slide_height = prs.slide_height

    for slide in prs.slides:
        shapes_to_remove = []

        for shape in slide.shapes:
            try:
                shape_type = shape.shape_type

                # Remove huge decorative auto shapes
                if shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE:
                    if (
                        shape.width > slide_width * 0.30
                        and shape.height > slide_height * 0.30
                    ):
                        shapes_to_remove.append(shape)

                # Remove full-slide decorative images
                elif shape_type == MSO_SHAPE_TYPE.PICTURE:
                    if (
                        shape.width > slide_width * 0.90
                        and shape.height > slide_height * 0.90
                    ):
                        shapes_to_remove.append(shape)

            except Exception:
                continue

        # Remove safely
        for shape in shapes_to_remove:
            try:
                sp = shape._element
                sp.getparent().remove(sp)
            except Exception:
                pass

    cleaned_ppt = input_ppt.replace(".pptx", "_cleaned.pptx")
    prs.save(cleaned_ppt)

    return cleaned_ppt


def render_ppt_slides_to_images(ppt_path):
    """
    Convert PPT slides to images:
    1. Remove PPT background/theme
    2. Convert cleaned PPT → PDF
    3. Convert PDF → images
    4. Skip title slides
    """

    temp_dir = tempfile.mkdtemp()

    try:
        # Step 1: clean ppt background
        cleaned_ppt = remove_ppt_background(ppt_path)

        # Step 2: convert cleaned ppt -> pdf
        subprocess.run([
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            cleaned_ppt,
            "--outdir",
            temp_dir
        ], check=True)

        generated_pdf = [
            os.path.join(temp_dir, f)
            for f in os.listdir(temp_dir)
            if f.endswith(".pdf")
        ][0]

        # Step 3: pdf -> images
        pages = convert_from_path(
            generated_pdf,
            dpi=200
        )

        final_images = []

        for i, page in enumerate(pages):
            img_path = os.path.join(
                temp_dir,
                f"slide_{i+1}.png"
            )

            page.save(img_path, "PNG")

            # Step 4: skip title slides
            if is_title_slide(img_path):
                print(f"Skipping title slide: {i+1}")
                continue

            final_images.append(img_path)

        return final_images

    finally:
        # Cleanup cleaned PPT
        cleaned_ppt_path = ppt_path.replace(".pptx", "_cleaned.pptx")

        if os.path.exists(cleaned_ppt_path):
            try:
                os.remove(cleaned_ppt_path)
            except Exception:
                pass
