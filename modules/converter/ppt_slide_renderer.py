import os
import tempfile
import subprocess

from pdf2image import convert_from_path
from PIL import Image
from pptx import Presentation
from pptx.util import Inches


def is_useless_slide(img_path):
    """
    Skip:
    - blank slides
    - thank you slides
    """
    try:
        img = Image.open(img_path).convert("L")

        hist = img.histogram()

        white_pixels = hist[255]
        total_pixels = sum(hist)

        white_ratio = white_pixels / total_pixels

        if white_ratio > 0.90:
            return True

        return False

    except:
        return False


def convert_original_ppt_to_images(ppt_path, temp_dir):
    """
    Convert original PPT -> PDF -> images
    """
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

    pages = convert_from_path(pdf_path, dpi=200)

    image_paths = []

    for i, page in enumerate(pages):
        img_path = os.path.join(temp_dir, f"original_slide_{i+1}.png")
        page.save(img_path, "PNG")

        if is_useless_slide(img_path):
            print(f"Skipping useless slide {i+1}")
            continue

        image_paths.append(img_path)

    return image_paths


def create_blank_ppt_with_images(image_paths, temp_dir):
    """
    Create new blank PPT with only slide images
    """
    prs = Presentation()

    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6]

    for img_path in image_paths:
        slide = prs.slides.add_slide(blank_layout)

        slide.shapes.add_picture(
            img_path,
            0,
            0,
            width=prs.slide_width,
            height=prs.slide_height
        )

    output_ppt = os.path.join(temp_dir, "cleaned_output.pptx")
    prs.save(output_ppt)

    return output_ppt


def convert_clean_ppt_to_images(clean_ppt, temp_dir):
    """
    Convert cleaned PPT -> PDF -> final images
    """
    subprocess.run([
        "libreoffice",
        "--headless",
        "--convert-to",
        "pdf",
        clean_ppt,
        "--outdir",
        temp_dir
    ], check=True)

    pdf_files = [
        os.path.join(temp_dir, f)
        for f in os.listdir(temp_dir)
        if f.endswith(".pdf")
        and "cleaned_output" in f
    ]

    if not pdf_files:
        raise Exception("Final PDF conversion failed")

    pdf_path = pdf_files[0]

    pages = convert_from_path(pdf_path, dpi=200)

    final_images = []

    for i, page in enumerate(pages):
        img_path = os.path.join(temp_dir, f"final_slide_{i+1}.png")
        page.save(img_path, "PNG")
        final_images.append(img_path)

    return final_images


def render_ppt_slides_to_images(ppt_path):
    temp_dir = tempfile.mkdtemp()

    try:
        # Step 1
        original_images = convert_original_ppt_to_images(
            ppt_path,
            temp_dir
        )

        if not original_images:
            return []

        # Step 2
        clean_ppt = create_blank_ppt_with_images(
            original_images,
            temp_dir
        )

        # Step 3
        final_images = convert_clean_ppt_to_images(
            clean_ppt,
            temp_dir
        )

        return final_images

    except Exception as e:
        print(f"PPT processing failed: {e}")
        return []
