import os
import tempfile
import aspose.slides as slides


def render_ppt_slides_to_images(ppt_path):
    """
    Render complete PPT slides as images.
    Preserves:
    - text boxes
    - arrows
    - shapes
    - annotations
    - screenshots
    - connectors
    - exact layout
    """

    output_dir = tempfile.mkdtemp()
    image_paths = []

    with slides.Presentation(ppt_path) as presentation:

        for index, slide in enumerate(presentation.slides):
            img_path = os.path.join(
                output_dir,
                f"slide_{index+1}.png"
            )

            slide.get_thumbnail(2, 2).save(img_path)

            image_paths.append(img_path)

    return image_paths
