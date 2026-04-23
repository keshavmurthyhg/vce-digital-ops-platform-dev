from modules.report.renderers.pdf_renderer import generate_pdf_doc
from modules.report.renderers.word_renderer import generate_word_doc


# ---------------- COMMON HELPERS ---------------- #

def clean_text(text):
    if not text:
        return ""
    import re
    return re.sub(r"How does the user want.*?\d+", "", str(text), flags=re.I).strip()


def format_date(date_str):
    if not date_str:
        return ""

    from datetime import datetime

    try:
        return datetime.strptime(str(date_str), "%Y-%m-%d").strftime("%d-%b-%Y")
    except:
        return str(date_str)


def safe_images(images):
    if not isinstance(images, dict):
        return {"root": [], "l2": [], "res": []}
    return images


# ---------------- PDF ENTRY ---------------- #

def generate_pdf(data, root, l2, res, images=None):
    """
    Main entry for PDF generation
    """
    images = safe_images(images)

    return generate_pdf_doc(
        data=data,
        root=root,
        l2=l2,
        res=res,
        images=images
    )


# ---------------- WORD ENTRY ---------------- #

def generate_word_doc_wrapper(data, root, l2, res, images=None):
    """
    Main entry for Word generation
    """
    images = safe_images(images)

    return generate_word_doc(
        data=data,
        root=root,
        l2=l2,
        res=res,
        images=images
    )
