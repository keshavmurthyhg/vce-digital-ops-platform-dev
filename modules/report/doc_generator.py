from modules.report.renderers.pdf_renderer import generate_pdf_doc
from modules.report.renderers.word_renderer import generate_word_doc
from modules.report.utils import format_description


def prepare_data(data):
    """
    Central place for all sanitization & formatting
    """
    safe_data = data.copy()

    safe_data["description"] = format_description(data.get("description"))

    return safe_data

def safe_images(images):
    if not isinstance(images, dict):
        return {"root": [], "l2": [], "res": []}
    return images


def generate_pdf(data, root, l2, res, images=None):
    images = safe_images(images)

    return generate_pdf_doc(
        data=data,
        root=root,
        l2=l2,
        res=res,
        images=images
    )


def generate_word_doc_wrapper(data, root, l2, res, images=None):
    images = safe_images(images)

    return generate_word_doc(
        data=data,
        root=root,
        l2=l2,
        res=res,
        images=images
    )
