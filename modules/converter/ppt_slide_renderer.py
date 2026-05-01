import os
import tempfile


def render_ppt_slides_to_images(ppt_path):
    import aspose.slides as slides

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
