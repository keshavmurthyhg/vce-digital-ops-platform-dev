import os
import tempfile
import uuid
import subprocess

from pdf2image import convert_from_path
from PIL import Image, ImageChops


def is_title_slide(img_path):
    """
    Detect title slides:
    mostly white background + very little actual content
    """
    img = Image.open(img_path).convert("RGB")
    width, height = img.size

    # Crop center area
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

    # Title slides usually mostly white
    return white_ratio > 0.85


def crop_white_and_theme(img_path):
    """
    Remove:
    - white margins
    - PPT decorative blue side panels
    """
    img = Image.open(img_path).convert("RGB")

    # Remove left/right theme borders
    width, height = img.size
    img = img.crop((
        int(width * 0.08),   # remove left blue design
        0,
        int(width * 0.92),   # remove right blue design
        height
    ))

    # Remove white outer margins
    bg = Image.new(img.mode, img.size, (255, 255, 255))
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()

    if bbox:
        img = img.crop(bbox)

    cleaned_path = img_path.replace(".png", "_clean.png")
    img.save(cleaned_path)

    return cleaned_path


def render_ppt_slides_to_images(ppt_path):
    temp_dir = tempfile.mkdtemp()

    pdf_path = os.path.join(
        temp_dir,
        f"{uuid.uuid4()}.pdf"
    )

    # Convert PPT → PDF
    subprocess.run([
        "libreoffice",
        "--headless",
        "--convert-to",
        "pdf",
        ppt_path,
        "--outdir",
        temp_dir
    ], check=True)

    generated_pdf = [
        os.path.join(temp_dir, f)
        for f in os.listdir(temp_dir)
        if f.endswith(".pdf")
    ][0]

    pages = convert_from_path(generated_pdf, dpi=200)

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

        cleaned = crop_white_and_theme(img_path)
        final_images.append(cleaned)

    return final_images
