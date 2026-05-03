import os
import tempfile
import subprocess
import copy

from pdf2image import convert_from_path
from PIL import Image
from pptx import Presentation


# -----------------------------
# Detect title slides
# -----------------------------
def is_title_slide(img_path):
    """
    Skip title slides that contain very little content
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
        histogram = gray.histogram()

        white_pixels = histogram[255]
        total_pixels = sum(histogram)

        white_ratio = white_pixels / total_pixels

        return white_ratio > 0.90

    except Exception:
        return False


# -----------------------------
# Find blank layout
# -----------------------------
def get_blank_layout(prs):
    """
    Return blank slide layout if available
    """
    for layout in prs.slide_layouts:
        try:
            if layout.name.lower() == "blank":
                return layout
        except:
            continue

    # fallback → last layout
    return prs.slide_layouts[-1]


# -----------------------------
# Clone shapes
# -----------------------------
def clone_shapes(source_slide, target_slide):
    """
    Copy all user content from original slide
    into blank slide
    """
    for shape in source_slide.shapes:
        try:
            el = copy.deepcopy(shape.element)
            target_slide.shapes._spTree.insert_element_before(
                el,
                'p:extLst'
            )
        except Exception:
            continue


# -----------------------------
# Remove original slides
# -----------------------------
def remove_slide(prs, index):
    slide_id = prs.slides._sldIdLst[index]
    prs.part.drop_rel(slide_id.rId)
    prs.slides._sldIdLst.remove(slide_id)


# -----------------------------
# Create blank-layout PPT
# -----------------------------
def convert_to_blank_layout(input_ppt):
    """
    Rebuild presentation using blank slides only
    This removes:
    - theme backgrounds
    - master templates
    - footer graphics
    - decorative layouts
    """
    prs = Presentation(input_ppt)

    blank_layout = get_blank_layout(prs)

    original_slides = list(prs.slides)

    # Create new blank slides
    for slide in original_slides:
        new_slide = prs.slides.add_slide(blank_layout)
        clone_shapes(slide, new_slide)

    # Remove original slides
    original_count = len(original_slides)

    for i in range(original_count):
        remove_slide(prs, 0)

    cleaned_ppt = input_ppt.replace(
        ".pptx",
        "_cleaned.pptx"
    )

    prs.save(cleaned_ppt)

    return cleaned_ppt


# -----------------------------
# Render PPT → images
# -----------------------------
def render_ppt_slides_to_images(ppt_path):
    temp_dir = tempfile.mkdtemp()

    try:
        # Step 1 → rebuild using blank layout
        cleaned_ppt = convert_to_blank_layout(ppt_path)

        # Step 2 → convert to PDF
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

        # Step 3 → PDF to images
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
