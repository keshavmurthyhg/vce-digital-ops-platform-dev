import os
import tempfile
import uuid

from pdf2image import convert_from_path

def render_ppt_slides_to_images(ppt_path):
    temp_dir = tempfile.mkdtemp()

    # convert ppt -> pdf
    subprocess.run([
        "libreoffice",
        "--headless",
        "--convert-to",
        "pdf",
        ppt_path,
        "--outdir",
        temp_dir
    ], check=True)

    pdf_file = None

    for file in os.listdir(temp_dir):
        if file.endswith(".pdf"):
            pdf_file = os.path.join(temp_dir, file)
            break

    if not pdf_file:
        raise Exception("PDF conversion failed")

    pages = convert_from_path(pdf_file, dpi=200)

    image_paths = []

    for i, page in enumerate(pages):
        img_path = os.path.join(temp_dir, f"slide_{i+1}.png")
        page.save(img_path, "PNG")
        image_paths.append(img_path)

    return image_paths


from PIL import Image

def make_white_background(image_path):
    img = Image.open(image_path).convert("RGBA")

    white_bg = Image.new(
        "RGBA",
        img.size,
        (255, 255, 255, 255)
    )

    white_bg.paste(img, (0, 0), img)
    white_bg.convert("RGB").save(image_path)
