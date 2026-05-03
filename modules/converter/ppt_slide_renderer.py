import os
import tempfile
import subprocess

from pdf2image import convert_from_path
from PIL import Image


def should_skip_slide(img_path):
    """
    Skip:
    - thank you slides
    - title slides
    - mostly blank/template slides
    """
    try:
        img = Image.open(img_path).convert("RGB")

        width, height = img.size

        # Ignore footer area
        content_region = img.crop((
            width * 0.05,
            height * 0.05,
            width * 0.95,
            height * 0.85
        ))

        gray = content_region.convert("L")
        hist = gray.histogram()

        total_pixels = sum(hist)
        white_pixels = hist[255]

        white_ratio = white_pixels / total_pixels

        # Skip almost empty slides
        if white_ratio > 0.88:
            return True

        # Detect dark theme-only slides
        dark_pixels = sum(hist[:40])
        dark_ratio = dark_pixels / total_pixels

        if dark_ratio > 0.55:
            return True

        return False

    except Exception as e:
        print(f"Slide detection error: {e}")
        return False


def render_ppt_slides_to_images(ppt_path):
    temp_dir = tempfile.mkdtemp()

    try:
        # Convert original PPT directly to PDF
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
            dpi=200
        )

        final_images = []

        for i, page in enumerate(pages):
            img_path = os.path.join(
                temp_dir,
                f"slide_{i+1}.png"
            )

            page.save(img_path, "PNG")

            if should_skip_slide(img_path):
                print(f"Skipping theme/title slide {i+1}")
                continue

            final_images.append(img_path)

        print(f"Final usable slides: {len(final_images)}")

        return final_images

    except Exception as e:
        print(f"PPT rendering failed: {e}")
        return []
