import os
import copy
import tempfile
import subprocess

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pdf2image import convert_from_path


# -----------------------------------
# Skip thank you slides
# -----------------------------------
def should_skip_slide(slide):
    texts = []

    for shape in slide.shapes:
        try:
            if hasattr(shape, "text"):
                txt = shape.text.strip().lower()
                if txt:
                    texts.append(txt)
        except:
            pass

    combined = " ".join(texts).strip()

    if combined == "thank you":
        return True

    if combined == "questions":
        return True

    return False


# -----------------------------------
# Detect full slide template background
# -----------------------------------
def is_background_shape(shape, slide_width, slide_height):
    try:
        if shape.shape_type not in [
            MSO_SHAPE_TYPE.PICTURE,
            MSO_SHAPE_TYPE.AUTO_SHAPE
        ]:
            return False

        if (
            shape.width >= slide_width * 0.90
            and shape.height >= slide_height * 0.90
            and shape.left <= slide_width * 0.05
            and shape.top <= slide_height * 0.05
        ):
            return True

        return False

    except:
        return False


# -----------------------------------
# Create cleaned PPT
# -----------------------------------
def create_clean_ppt(ppt_path):
    source_prs = Presentation(ppt_path)

    clean_prs = Presentation()
    clean_prs.slide_width = source_prs.slide_width
    clean_prs.slide_height = source_prs.slide_height

    blank_layout = clean_prs.slide_layouts[6]

    for slide_index, slide in enumerate(source_prs.slides):
        print(f"Processing slide {slide_index+1}")

        if should_skip_slide(slide):
            print("Skipping thank you/questions slide")
            continue

        new_slide = clean_prs.slides.add_slide(blank_layout)

        for shape in slide.shapes:
            try:
                # Remove only full slide background
                if is_background_shape(
                    shape,
                    source_prs.slide_width,
                    source_prs.slide_height
                ):
                    print("Skipping background shape")
                    continue

                # Clone EVERYTHING else exactly as-is
                el = shape.element
                new_el = copy.deepcopy(el)

                new_slide.shapes._spTree.insert_element_before(
                    new_el,
                    "p:extLst"
                )

            except Exception as e:
                print(
                    f"Failed copying shape on slide "
                    f"{slide_index+1}: {e}"
                )

    temp_dir = tempfile.mkdtemp()

    clean_ppt_path = os.path.join(
        temp_dir,
        "clean_ppt.pptx"
    )

    clean_prs.save(clean_ppt_path)

    return clean_ppt_path, temp_dir


# -----------------------------------
# Convert PPT → images
# -----------------------------------
def render_ppt_slides_to_images(ppt_path):
    try:
        clean_ppt_path, temp_dir = create_clean_ppt(ppt_path)

        subprocess.run([
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            clean_ppt_path,
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
            final_images.append(img_path)

        print(f"Generated {len(final_images)} images")

        return final_images

    except Exception as e:
        print(f"PPT rendering failed: {e}")
        return []
