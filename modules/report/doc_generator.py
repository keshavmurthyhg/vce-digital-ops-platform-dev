from modules.report.renderers.pdf_renderer import generate_pdf_doc
from modules.report.renderers.word_renderer import generate_word_doc


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
