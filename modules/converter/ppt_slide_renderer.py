import os
import copy
import tempfile
import subprocess

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pdf2image import convert_from_path


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

    combined = " ".join(texts)

    return combined.strip() in ["thank you", "questions"]


def is_background_picture(shape, slide_width, slide_height):
    try:
        if shape.shape_type != MSO_SHAPE_TYPE.PICTURE:
            return False

        return (
            shape.width >= slide_width * 0.9
            and shape.height >= slide_height * 0.9
            and shape.left <= slide_width * 0.05
            and shape.top <= slide_height * 0.05
        )
    except:
        return False


def add_picture(shape, new_slide):
    try:
        image = shape.image
        image_bytes = image.blob

        temp_img = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=f".{image.ext}"
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
        print(f"Picture extraction failed: {e}")
        return False


def process_group_shape(group_shape, new_slide):
    try:
        for subshape in group_shape.shapes:

            if subshape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                try:
                    image = subshape.image
                    image_bytes = image.blob

                    temp_img = tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=f".{image.ext}"
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
                    print(f"Group image failed: {e}")

            else:
                try:
                    el = subshape.element
                    new_el = copy.deepcopy(el)

                    new_slide.shapes._spTree.insert_element_before(
                        new_el,
                        "p:extLst"
                    )
                except Exception as e:
                    print(f"Group annotation failed: {e}")

    except Exception as e:
        print(f"Group processing failed: {e}")


def create_clean_ppt(ppt_path):
    source_prs = Presentation(ppt_path)

    clean_prs = Presentation()
    clean_prs.slide_width = source_prs.slide_width
    clean_prs.slide_height = source_prs.slide_height

    blank_layout = clean_prs.slide_layouts[6]

    for idx, slide in enumerate(source_prs.slides):
        print(f"Processing slide {idx+1}")

        if should_skip_slide(slide):
            print("Skipping thank you slide")
            continue

        new_slide = clean_prs.slides.add_slide(blank_layout)

        for shape in slide.shapes:
            try:
                # Handle normal screenshots/images
                if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                    if is_background_picture(
                        shape,
                        source_prs.slide_width,
                        source_prs.slide_height
                    ):
                        print("Skipping background image")
                        continue

                    success = add_picture(shape, new_slide)

                    if not success:
                        print(f"Image failed on slide {idx+1}")

                # Handle grouped screenshots
                elif shape.shape_type == MSO_SHAPE_TYPE.GROUP:
                    process_group_shape(shape, new_slide)

                # Handle textboxes/arrows/lines
                else:
                    el = shape.element
                    new_el = copy.deepcopy(el)

                    new_slide.shapes._spTree.insert_element_before(
                        new_el,
                        "p:extLst"
                    )

            except Exception as e:
                print(f"Shape failed: {e}")

    temp_dir = tempfile.mkdtemp()

    clean_ppt_path = os.path.join(
        temp_dir,
        "clean_ppt.pptx"
    )

    clean_prs.save(clean_ppt_path)

    return clean_ppt_path, temp_dir


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
        print(f"PPT conversion failed: {e}")
        return []
