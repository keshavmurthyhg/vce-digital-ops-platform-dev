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
    mostly white background + very little content
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
    Remove removable shapes from PPT
    """
    prs = Presentation(input_ppt)

    slide_width = prs.slide_width
    slide_height = prs.slide_height

    for slide in prs.slides:
        shapes_to_remove = []

        for shape in slide.shapes:
            try:
                shape_type = shape.shape_type

                # grouped template objects
                if shape_type == MSO_SHAPE_TYPE.GROUP:
                    if shape.top > slide_height * 0.55:
                        shapes_to_remove.append(shape)

                # large decorative shapes
                elif shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE:
                    if (
                        shape.width > slide_width * 0.30
                        and shape.height > slide_height * 0.25
                    ):
                        shapes_to_remove.append(shape)

                    elif (
                        shape.top > slide_height * 0.65
                        and (
                            shape.left < slide_width * 0.25
                            or shape.left > slide_width * 0.70
                        )
                    ):
                        shapes_to_remove.append(shape)

            except Exception:
                continue

        for shape in shapes_to_remove:
            try:
                sp = shape._element
                sp.getparent().remove(sp)
            except:
                pass

    cleaned_ppt = input_ppt.replace(".pptx", "_cleaned.pptx")
    prs.save(cleaned_ppt)

    return cleaned_ppt


def crop_bottom_template_if_needed(img_path):
    """
    Remove bottom blue PPT template after image generation
    ONLY if large blank/template area exists
    """
    img = Image.open(img_path)
    width, height = img.size

    bottom_section = img.crop((
        0,
        int(height * 0.70),
        width,
        height
    ))

    pixels = bottom_section.convert("RGB").getdata()

    blue_pixels = 0

    for r, g, b in pixels:
        if b > r + 30 and b > g + 30:
            blue_pixels += 1

    blue_ratio = blue_pixels / len(pixels)

    # Crop only when template dominates bottom area
    if blue_ratio > 0.08:
        crop_height = int(height * 0.70)

        cropped = img.crop((
            0,
            0,
            width,
            crop_height
        ))

        cropped.save(img_path)
        print(f"Removed bottom template from {img_path}")


def render_ppt_slides_to_images(ppt_path):
    """
    Convert PPT slides → images
    """
    temp_dir = tempfile.mkdtemp()

    try:
        cleaned_ppt = remove_ppt_background(ppt_path)

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

            # Skip title slides
            if is_title_slide(img_path):
                print(f"Skipping title slide: {i+1}")
                continue

            # Final cleanup for leftover blue template
            crop_bottom_template_if_needed(img_path)

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
