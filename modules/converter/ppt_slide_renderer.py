import os
import tempfile
import subprocess

from pdf2image import convert_from_path
from PIL import Image
from pptx import Presentation
from pptx.enum.shapes import PP_PLACEHOLDER


# -----------------------------
# Detect title slides
# -----------------------------
def is_title_slide(img_path):
    try:
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

        return white_ratio > 0.90

    except Exception:
        return False


# -----------------------------
# Remove slide background
# -----------------------------
def remove_background_and_placeholders(input_ppt):
    """
    Remove only:
    - slide background
    - title placeholders
    - footer placeholders

    Keep:
    - screenshots
    - annotations
    - arrows
    - text boxes
    - lines
    """

    prs = Presentation(input_ppt)

    for slide in prs.slides:
        try:
            # reset background
            slide.background.fill.solid()
            slide.background.fill.fore_color.rgb = None
        except:
            pass

        shapes_to_remove = []

        for shape in slide.shapes:
            try:
                if shape.is_placeholder:
                    placeholder_type = shape.placeholder_format.type

                    if placeholder_type in [
                        PP_PLACEHOLDER.TITLE,
                        PP_PLACEHOLDER.CENTER_TITLE,
                        PP_PLACEHOLDER.FOOTER,
                        PP_PLACEHOLDER.DATE,
                        PP_PLACEHOLDER.SLIDE_NUMBER
                    ]:
                        shapes_to_remove.append(shape)

            except:
                continue

        for shape in shapes_to_remove:
            try:
                sp = shape._element
                sp.getparent().remove(sp)
            except:
                pass

    cleaned_ppt = input_ppt.replace(
        ".pptx",
        "_cleaned.pptx"
    )

    prs.save(cleaned_ppt)

    return cleaned_ppt


# -----------------------------
# Convert PPT -> images
# -----------------------------
def render_ppt_slides_to_images(ppt_path):
    temp_dir = tempfile.mkdtemp()

    try:
        # Step 1
        cleaned_ppt = remove_background_and_placeholders(ppt_path)

        # Step 2
        subprocess.run([
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            cleaned_ppt,
            "--outdir",
            temp_dir
        ], check=True)

        pdf_files = [
            os.path.join(temp_dir, f)
            for f in os.listdir(temp_dir)
            if f.endswith(".pdf")
        ]

        if not pdf_files:
            raise Exception("PDF conversion failed")

        generated_pdf = pdf_files[0]

        # Step 3
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

            if is_title_slide(img_path):
                print(f"Skipping title slide {i+1}")
                continue

            final_images.append(img_path)

        return final_images

    finally:
        cleaned_ppt = ppt_path.replace(
            ".pptx",
            "_cleaned.pptx"
        )

        if os.path.exists(cleaned_ppt):
            try:
                os.remove(cleaned_ppt)
            except:
                pass
