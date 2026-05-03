import os
import tempfile
import subprocess

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pdf2image import convert_from_path


# -----------------------------------
# Skip unwanted slides
# -----------------------------------
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


# -----------------------------------
# Detect full slide background images
# -----------------------------------
def is_background_picture(shape, slide_width, slide_height):
    try:
        if shape.shape_type != MSO_SHAPE_TYPE.PICTURE:
            return False

        # full slide template/background detection
        if (
            shape.width >= slide_width * 0.90 and
            shape.height >= slide_height * 0.90 and
            shape.left <= slide_width * 0.05 and
            shape.top <= slide_height * 0.05
        ):
            return True

        return False

    except Exception:
        return False


# -----------------------------------
# Extract normal picture
# -----------------------------------
def add_picture_to_slide(shape, new_slide):
    try:
        image = shape.image
        image_bytes = image.blob

        temp_img = tempfile.NamedTemporaryFile(
            delete=False,
            suffix="." + image.ext
        )

        temp_img.write(image_bytes)
        temp_img.close()

        new_slide.shapes.add_picture(
            temp_img.name,
            shape.left,
            shape.top,
            shape.width,
            shape.height
        )

        return True

    except Exception as e:
        print(f"Normal picture extraction failed: {e}")
        return False


# -----------------------------------
# Extract grouped pictures
# -----------------------------------
def add_group_pictures(group_shape, new_slide):
    try:
        print("Processing grouped shapes")

        for subshape in group_shape.shapes:
            try:
                if subshape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                    image = subshape.image
                    image_bytes = image.blob

                    temp_img = tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix="." + image.ext
                    )

                    temp_img.write(image_bytes)
                    temp_img.close()

                    new_slide.shapes.add_picture(
                        temp_img.name,
                        group_shape.left + subshape.left,
                        group_shape.top + subshape.top,
                        subshape.width,
                        subshape.height
                    )

            except Exception as e:
                print(f"Grouped image extraction failed: {e}")

    except Exception as e:
        print(f"Group processing failed: {e}")


# -----------------------------------
# Create clean PPT
# -----------------------------------
import copy
import os
import tempfile
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE


def create_clean_ppt(ppt_path):
    source_prs = Presentation(ppt_path)

    clean_prs = Presentation()
    clean_prs.slide_width = source_prs.slide_width
    clean_prs.slide_height = source_prs.slide_height

    blank_layout = clean_prs.slide_layouts[6]

    for slide_index, slide in enumerate(source_prs.slides):
        print(f"Processing slide {slide_index + 1}")

        if should_skip_slide(slide):
            print("Skipping unwanted slide")
            continue

        new_slide = clean_prs.slides.add_slide(blank_layout)

        shapes_to_remove = []

        for shape in slide.shapes:
            try:
                # clone original shape completely
                el = shape.element
                new_el = copy.deepcopy(el)
                new_slide.shapes._spTree.insert_element_before(
                    new_el,
                    'p:extLst'
                )

                # mark only full-slide background images
                if (
                    shape.shape_type == MSO_SHAPE_TYPE.PICTURE
                    and is_background_picture(
                        shape,
                        source_prs.slide_width,
                        source_prs.slide_height
                    )
                ):
                    shapes_to_remove.append(
                        new_slide.shapes[-1]
                    )

            except Exception as e:
                print(f"Shape clone failed: {e}")

        # remove only background shapes
        for bg_shape in shapes_to_remove:
            try:
                sp = bg_shape._element
                sp.getparent().remove(sp)
            except Exception as e:
                print(f"Background removal failed: {e}")

    temp_dir = tempfile.mkdtemp()

    clean_ppt_path = os.path.join(
        temp_dir,
        "clean_ppt.pptx"
    )

    clean_prs.save(clean_ppt_path)

    return clean_ppt_path, temp_dir
# -----------------------------------
# Convert clean PPT -> images
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

        print(f"Generated {len(final_images)} slide images")

        return final_images

    except Exception as e:
        print(f"PPT render failed: {e}")
        return []
