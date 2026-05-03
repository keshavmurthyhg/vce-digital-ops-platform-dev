import os
import tempfile
import subprocess

from pdf2image import convert_from_path
from PIL import Image
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE


def is_title_slide(img_path):
    """
    Detect title slides:
    mostly white background with minimal content
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


def should_keep_shape(shape, slide_width, slide_height):
    """
    Keep useful shapes:
    - screenshots/images
    - annotations
    - arrows
    - lines
    - textboxes
    - grouped objects
    """

    try:
        shape_type = shape.shape_type

        # Always keep screenshots/images
        if shape_type == MSO_SHAPE_TYPE.PICTURE:
            return True

        # Keep text boxes
        if shape.has_text_frame:
            return True

        # Keep lines/arrows/connectors
        if shape_type == MSO_SHAPE_TYPE.LINE:
            return True

        # Keep grouped content
        if shape_type == MSO_SHAPE_TYPE.GROUP:
            return True

        # Keep small annotation rectangles/callouts
        if shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE:
            if (
                shape.width < slide_width * 0.35
                and shape.height < slide_height * 0.25
            ):
                return True

        return False

    except Exception:
        return True


def clean_slide_background(input_ppt):
    """
    Remove decorative/template shapes while keeping useful content
    """
    prs = Presentation(input_ppt)

    slide_width = prs.slide_width
    slide_height = prs.slide_height

    for slide in prs.slides:
        shapes_to_remove = []

        for shape in slide.shapes:
            try:
                if not should_keep_shape(
                    shape,
                    slide_width,
                    slide_height
                ):
                    shapes_to_remove.append(shape)

            except Exception:
                continue

        for shape in shapes_to_remove:
            try:
                sp = shape._element
                sp.getparent().remove(sp)
            except Exception:
                pass

    cleaned_ppt = input_ppt.replace(
        ".pptx",
        "_cleaned.pptx"
    )

    prs.save(cleaned_ppt)

    return cleaned_ppt


def render_ppt_slides_to_images(ppt_path):
    """
    Convert PPT slides → cleaned images
    """
    temp_dir = tempfile.mkdtemp()

    try:
        # Step 1: clean PPT
        cleaned_ppt = clean_slide_background(ppt_path)

        # Step 2: PPT → PDF
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

        # Step 3: PDF → images
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

            page.save(
                img_path,
                "PNG"
            )

            # Step 4: skip title slides
            if is_title_slide(img_path):
                print(f"Skipping title slide: {i+1}")
                continue

            final_images.append(img_path)

        return final_images

    finally:
        cleaned_ppt_path = ppt_path.replace(
            ".pptx",
            "_cleaned.pptx"
        )

        if os.path.exists(cleaned_ppt_path):
            try:
                os.remove(cleaned_ppt_path)
            except Exception:
                pass
