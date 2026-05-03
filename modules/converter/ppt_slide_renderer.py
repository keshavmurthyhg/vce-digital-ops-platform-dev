import os
import tempfile
import subprocess
import copy

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pdf2image import convert_from_path


def is_title_or_thankyou_slide(slide):
    text_content = []

    for shape in slide.shapes:
        if hasattr(shape, "text"):
            text_content.append(shape.text.strip().lower())

    combined = " ".join(text_content)

    if "thank you" in combined:
        return True

    if len(combined) < 15:
        return True

    return False


def clone_shape(source_shape, target_slide):
    try:
        el = source_shape.element
        new_el = copy.deepcopy(el)
        target_slide.shapes._spTree.insert_element_before(new_el, 'p:extLst')
    except Exception as e:
        print(f"Shape copy failed: {e}")


def create_clean_ppt(original_ppt):
    source_prs = Presentation(original_ppt)

    clean_prs = Presentation()
    clean_prs.slide_width = source_prs.slide_width
    clean_prs.slide_height = source_prs.slide_height

    blank_layout = clean_prs.slide_layouts[6]

    for slide in source_prs.slides:

        if is_title_or_thankyou_slide(slide):
            print("Skipping title/thank you slide")
            continue

        new_slide = clean_prs.slides.add_slide(blank_layout)

        for shape in slide.shapes:
            try:
                # Skip placeholders only
                if shape.is_placeholder:
                    continue

                # Skip full-slide background images
                if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                    try:
                        left = shape.left
                        top = shape.top
                        width = shape.width
                        height = shape.height

                        slide_w = source_prs.slide_width
                        slide_h = source_prs.slide_height

                        # If image covers almost entire slide → treat as theme bg
                        if (
                            width >= slide_w * 0.90 and
                            height >= slide_h * 0.90 and
                            left <= slide_w * 0.05 and
                            top <= slide_h * 0.05
                        ):
                            print("Skipping background image")
                            continue

                    except:
                        pass

                # Copy everything else
                el = shape.element
                new_el = copy.deepcopy(el)
                new_slide.shapes._spTree.insert_element_before(
                    new_el,
                    'p:extLst'
                )

            except Exception as e:
                print(f"Shape copy failed: {e}")
                continue

    temp_dir = tempfile.mkdtemp()
    clean_ppt_path = os.path.join(temp_dir, "cleaned_ppt.pptx")

    clean_prs.save(clean_ppt_path)

    return clean_ppt_path, temp_dir

def convert_clean_ppt_to_images(clean_ppt_path, temp_dir):
    subprocess.run([
        "libreoffice",
        "--headless",
        "--convert-to",
        "pdf",
        clean_ppt_path,
        "--outdir",
        temp_dir
    ], check=True)

    pdf_path = os.path.join(temp_dir, "cleaned_ppt.pdf")

    if not os.path.exists(pdf_path):
        raise Exception("PDF conversion failed")

    pages = convert_from_path(pdf_path, dpi=200)

    image_paths = []

    for i, page in enumerate(pages):
        img_path = os.path.join(temp_dir, f"slide_{i+1}.png")
        page.save(img_path, "PNG")
        image_paths.append(img_path)

    return image_paths


def render_ppt_slides_to_images(ppt_path):
    try:
        clean_ppt_path, temp_dir = create_clean_ppt(ppt_path)
        return convert_clean_ppt_to_images(clean_ppt_path, temp_dir)

    except Exception as e:
        print(f"PPT render failed: {e}")
        return []
