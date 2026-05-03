import os
import tempfile
import subprocess

from pdf2image import convert_from_path
from PIL import Image


def should_skip_slide(img_path):
    """
    Skip:
    - thank you slides
    - blank slides
    """

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
        hist = gray.histogram()

        white_pixels = hist[255]
        total_pixels = sum(hist)

        white_ratio = white_pixels / total_pixels

        if white_ratio > 0.92:
            return True

        return False

    except:
        return False


def render_ppt_slides_to_images(ppt_path):
    temp_dir = tempfile.mkdtemp()

    try:
        # -----------------------------
        # Step 1: PPT -> ODP
        # -----------------------------
        subprocess.run([
            "libreoffice",
            "--headless",
            "--convert-to",
            "odp",
            ppt_path,
            "--outdir",
            temp_dir
        ], check=True)

        odp_files = [
            os.path.join(temp_dir, f)
            for f in os.listdir(temp_dir)
            if f.endswith(".odp")
        ]

        if not odp_files:
            raise Exception("ODP conversion failed")

        odp_path = odp_files[0]

        print(f"ODP created: {odp_path}")

        # -----------------------------
        # Step 2: ODP -> PDF
        # -----------------------------
        subprocess.run([
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            odp_path,
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

        print(f"PDF created: {pdf_path}")

        # -----------------------------
        # Step 3: PDF -> images
        # -----------------------------
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
                print(f"Skipping blank/title slide {i+1}")
                continue

            final_images.append(img_path)

        print(f"Final slide count: {len(final_images)}")

        return final_images

    except Exception as e:
        print(f"PPT processing failed: {e}")
        return []
