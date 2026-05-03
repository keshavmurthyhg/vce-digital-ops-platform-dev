import os
import tempfile
import subprocess

from pptx import Presentation
from pdf2image import convert_from_path
from PIL import Image


def should_skip_slide(slide):
    texts = []

    for shape in slide.shapes:
        if hasattr(shape, "text"):
            txt = shape.text.strip().lower()
            if txt:
                texts.append(txt)

    combined_text = " ".join(texts)

    if "thank you" in combined_text:
        return True

    if "ppt slides" in combined_text:
        return True

    if "questions" in combined_text:
        return True

    return False


def crop_white_space(img_path):
    try:
        img = Image.open(img_path).convert("RGB")

        width, height = img.size

        # crop only footer area
        cropped = img.crop((
            0,
            0,
            width,
            int(height * 0.92)
        ))

        cropped.save(img_path)

    except Exception as e:
        print(f"Crop failed: {e}")


def render_ppt_slides_to_images(ppt_path):
    temp_dir = tempfile.mkdtemp()

    try:
        prs = Presentation(ppt_path)

        valid_indexes = []

        for i, slide in enumerate(prs.slides):
            if should_skip_slide(slide):
                print(f"Skipping slide {i+1}")
                continue

            valid_indexes.append(i)

        print(f"Valid slides: {valid_indexes}")

        subprocess.run([
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            ppt_path,
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

        pdf_path = pdf_files[0]

        pages = convert_from_path(
            pdf_path,
            dpi=220
        )

        final_images = []

        for i, page in enumerate(pages):
            if i not in valid_indexes:
                continue

            img_path = os.path.join(
                temp_dir,
                f"slide_{i+1}.png"
            )

            page.save(img_path, "PNG")

            crop_white_space(img_path)

            final_images.append(img_path)

        return final_images

    except Exception as e:
        print(f"PPT rendering failed: {e}")
        return []
