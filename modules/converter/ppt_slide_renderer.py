import os
import copy
import tempfile
from io import BytesIO

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE


# -----------------------------
# Detect thank you / closing slides
# -----------------------------
def is_thank_you_slide(slide):
    slide_text = ""

    for shape in slide.shapes:
        if hasattr(shape, "text"):
            slide_text += shape.text.lower()

    keywords = [
        "thank you",
        "thanks",
        "questions?",
        "q&a"
    ]

    return any(k in slide_text for k in keywords)


# -----------------------------
# Detect full slide background screenshots
# -----------------------------
def is_background_picture(shape, slide_width, slide_height):
    try:
        if shape.shape_type != MSO_SHAPE_TYPE.PICTURE:
            return False

        width_ratio = shape.width / slide_width
        height_ratio = shape.height / slide_height

        if width_ratio >= 0.90 and height_ratio >= 0.90:
            return True

        return False

    except:
        return False


# -----------------------------
# Add extracted image safely
# -----------------------------
def add_picture(shape, target_slide):
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


# -----------------------------
# Copy annotations/text/shapes
# -----------------------------
def copy_non_picture_shapes(source_slide, target_slide):
    for shape in source_slide.shapes:
        try:
            if shape.shape_type in [
                MSO_SHAPE_TYPE.PICTURE,
                MSO_SHAPE_TYPE.LINKED_PICTURE,
                MSO_SHAPE_TYPE.EMBEDDED_OLE_OBJECT,
                MSO_SHAPE_TYPE.OLE_OBJECT
            ]:
                continue

            el = copy.deepcopy(shape.element)

            target_slide.shapes._spTree.insert_element_before(
                el,
                "p:extLst"
            )

        except Exception as e:
            print(f"Shape copy failed: {e}")


# -----------------------------
# Full fallback → copy original slide
# -----------------------------
def fallback_to_original_slide(clean_prs, slide, blank_layout):
    try:
        fallback_slide = clean_prs.slides.add_slide(blank_layout)

        for original_shape in slide.shapes:
            try:
                el = copy.deepcopy(original_shape.element)

                fallback_slide.shapes._spTree.insert_element_before(
                    el,
                    "p:extLst"
                )

            except Exception as ex:
                print(f"Fallback shape failed: {ex}")

    except Exception as e:
        print(f"Fallback slide creation failed: {e}")


# -----------------------------
# Main renderer
# -----------------------------
def render_ppt_slides_to_images(ppt_path):
    source_prs = Presentation(ppt_path)

    clean_prs = Presentation()
    clean_prs.slide_width = source_prs.slide_width
    clean_prs.slide_height = source_prs.slide_height

    blank_layout = clean_prs.slide_layouts[6]

    # remove default slide
    if len(clean_prs.slides) > 0:
        rId = clean_prs.slides._sldIdLst[0].rId
        clean_prs.part.drop_rel(rId)
        del clean_prs.slides._sldIdLst[0]

    for idx, slide in enumerate(source_prs.slides):
        print(f"Processing slide {idx+1}")

        # Skip thank you slides
        if is_thank_you_slide(slide):
            print(f"Skipping thank you slide {idx+1}")
            continue

        slide_failed = False

        new_slide = clean_prs.slides.add_slide(blank_layout)

        for shape in slide.shapes:
            try:
                # --------------------------------
                # Standard picture
                # --------------------------------
                if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:

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

                    success = add_picture(shape, new_slide)

                    if not success:
                        slide_failed = True
                        break

                # --------------------------------
                # OLE / embedded screenshots
                # --------------------------------
                elif shape.shape_type in [
                    MSO_SHAPE_TYPE.LINKED_PICTURE,
                    MSO_SHAPE_TYPE.EMBEDDED_OLE_OBJECT,
                    MSO_SHAPE_TYPE.OLE_OBJECT
                ]:

                    print(
                        f"Processing embedded image "
                        f"on slide {idx+1}"
                    )

                    success = add_picture(shape, new_slide)

                    if not success:
                        slide_failed = True
                        break

                # --------------------------------
                # annotations/text/arrows
                # --------------------------------
                else:
                    try:
                        el = copy.deepcopy(shape.element)

                        new_slide.shapes._spTree.insert_element_before(
                            el,
                            "p:extLst"
                        )

                    except Exception as e:
                        print(
                            f"Annotation copy failed "
                            f"on slide {idx+1}: {e}"
                        )

            except Exception as e:
                print(
                    f"Slide {idx+1} failed: {e}"
                )
                slide_failed = True
                break

        # --------------------------------
        # Fallback for problematic slides
        # --------------------------------
        if slide_failed:
            print(
                f"Using fallback original slide "
                f"for slide {idx+1}"
            )

            try:
                rId = clean_prs.slides._sldIdLst[-1].rId
                clean_prs.part.drop_rel(rId)
                del clean_prs.slides._sldIdLst[-1]
            except:
                pass

            fallback_to_original_slide(
                clean_prs,
                slide,
                blank_layout
            )

    # --------------------------------
    # Save cleaned ppt
    # --------------------------------
    temp_dir = tempfile.mkdtemp()

    output_ppt = os.path.join(
        temp_dir,
        "cleaned_slides.pptx"
    )

    clean_prs.save(output_ppt)

    return output_ppt
