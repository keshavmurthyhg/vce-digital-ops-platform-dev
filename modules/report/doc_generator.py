from modules.report.doc_word import generate_word_doc
from modules.report.doc_pdf import generate_pdf


def generate_word(data, root, l2, res, images=None):
    return generate_word_doc(data, root, l2, res, images)


def generate_pdf_report(data, root, l2, res, images=None):
    return generate_pdf(data, root, l2, res, images)
