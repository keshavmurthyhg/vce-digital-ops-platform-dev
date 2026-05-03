import os
import tempfile
import subprocess

from pdf2image import convert_from_path
from PIL import Image
from pptx import Presentation

def should_skip_slide(img_path):
    """
    Skip:
    - blank slides
    - title slides
    - separator slides
    - thank you slides
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

        # Mostly blank slide
        if white_ratio > 0.88:
            return True

        # Dark theme slide
        dark_pixels = sum(hist[:40])
        dark_ratio = dark_pixels / total_pixels

        if dark_ratio > 0.55:
            return True

        # Detect very low-content slides
        non_white_pixels = total_pixels - white_pixels
        content_ratio = non_white_pixels / total_pixels

        # These are usually title/separator slides
        if content_ratio < 0.05:
            return True

        return False

    except Exception as e:
        print(f"Slide detection error: {e}")
        return False


def render_ppt_slides_to_images(ppt_path):
    temp_dir = tempfile.mkdtemp()

    try:
        # -----------------------------------
        # Step 1: Identify slides to skip
        # -----------------------------------
        prs = Presentation(ppt_path)

        skip_indexes = set()

        for idx, slide in enumerate(prs.slides):
            all_text = []

            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    txt = shape.text.strip().lower()
                    if txt:
                        all_text.append(txt)

            combined_text = " ".join(all_text)

            print(f"Slide {idx+1}: {combined_text}")

            # Skip thank you slides
            if "thank you" in combined_text:
                skip_indexes.add(idx)
                continue

            # Skip separator slides
            if "ppt slides" in combined_text:
                skip_indexes.add(idx)
                continue

            # Skip questions slide
            if "questions" in combined_text:
                skip_indexes.add(idx)
                continue

            # Skip title-only slides
            word_count = len(combined_text.split())

            if word_count <= 3:
                skip_indexes.add(idx)
                continue

        print(f"Skipping slides: {skip_indexes}")

        # -----------------------------------
        # Step 2: Convert full PPT -> PDF
        # -----------------------------------
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
            if i in skip_indexes:
                print(f"Skipping slide image {i+1}")
                continue

            img_path = os.path.join(
                temp_dir,
                f"slide_{i+1}.png"
            )

            page.save(img_path, "PNG")
            final_images.append(img_path)

        print(f"Final usable slides: {len(final_images)}")

        return final_images

    except Exception as e:
        print(f"PPT rendering failed: {e}")
        return []
