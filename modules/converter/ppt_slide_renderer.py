import os
import copy
import tempfile
from io import BytesIO

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE


# -----------------------------------------
# Detect thank you slides
# -----------------------------------------
def is_thank_you_slide(slide):
    try:
        slide_text = ""

        for shape in slide.shapes:
            if hasattr(shape, "text"):
                slide_text += str(shape.text).lower()

        keywords = [
            "thank you",
            "thanks",
            "questions?",
            "q&a"
        ]

        return any(k in slide_text for k in keywords)

    except Exception:
        return False


# -----------------------------------------
# Detect background screenshot
# -----------------------------------------
def is_background_picture(shape, slide_width, slide_height):
    try:
        if shape.shape_type != MSO_SHAPE_TYPE.PICTURE:
            return False

        width_ratio = shape.width / slide_width
        height_ratio = shape.height / slide_height

        # Full-slide template backgrounds
        if width_ratio >= 0.90 and height_ratio >= 0.90:
            return True

        return False

    except:
        return False


# -----------------------------------------
# Add image safely
# -----------------------------------------
def add_picture_to_slide(shape, target_slide):
    try:
        image_bytes = shape.image.blob

        target_slide.shapes.add_picture(
            BytesIO(image_bytes),
            shape.left,
            shape.top,
            shape.width,
            shape.height
        )

        return True

    except Exception as e:
        print(f"Image extraction failed: {e}")
        return False


# -----------------------------------------
# Copy annotation shapes
# -----------------------------------------
def copy_annotation_shape(shape, target_slide):
    try:
        element = copy.deepcopy(shape.element)

        target_slide.shapes._spTree.insert_element_before(
            element,
            "p:extLst"
        )

        return True

    except Exception as e:
        print(f"Annotation copy failed: {e}")
        return False


# -----------------------------------------
# Main renderer
# -----------------------------------------
def render_ppt_slides_to_images(ppt_path):
    source_prs = Presentation(ppt_path)

    clean_prs = Presentation()
    clean_prs.slide_width = source_prs.slide_width
    clean_prs.slide_height = source_prs.slide_height

    blank_layout = clean_prs.slide_layouts[6]

    # Remove default blank slide
    if len(clean_prs.slides) > 0:
        try:
            rId = clean_prs.slides._sldIdLst[0].rId
            clean_prs.part.drop_rel(rId)
            del clean_prs.slides._sldIdLst[0]
        except:
            pass

    for idx, slide in enumerate(source_prs.slides):
        print(f"Processing slide {idx+1}")

        # Skip thank you slide
        if is_thank_you_slide(slide):
            print(f"Skipping thank you slide {idx+1}")
            continue

        new_slide = clean_prs.slides.add_slide(blank_layout)

        for shape in slide.shapes:
            try:
                # -----------------------------------
                # Handle screenshots/images
                # -----------------------------------
                if shape.shape_type in [
                    MSO_SHAPE_TYPE.PICTURE
                ]:
                    if is_background_picture(
                        shape,
                        source_prs.slide_width,
                        source_prs.slide_height
                    ):
                        print(
                            f"Skipping background image "
                            f"on slide {idx+1}"
                        )
                        continue

                    success = add_picture_to_slide(
                        shape,
                        new_slide
                    )

                    if success:
                        print(
                            f"Image extracted "
                            f"on slide {idx+1}"
                        )

                # -----------------------------------
                # Handle annotations/arrows/textboxes
                # -----------------------------------
                else:
                    copy_annotation_shape(
                        shape,
                        new_slide
                    )

            except Exception as e:
                print(
                    f"Shape processing failed "
                    f"on slide {idx+1}: {e}"
                )

    # Save cleaned PPT
    temp_dir = tempfile.mkdtemp()

    output_ppt = os.path.join(
        temp_dir,
        "cleaned_slides.pptx"
    )

    clean_prs.save(output_ppt)

    print(f"Clean PPT saved: {output_ppt}")

    return output_ppt
