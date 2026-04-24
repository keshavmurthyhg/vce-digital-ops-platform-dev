from docx import Document
from io import BytesIO
import os

from modules.converter.ppt_to_doc import ppt_to_word
from modules.report.doc_generator import generate_word_doc


def generate_combined_report(ppt_path, snow_data, root, l2, res, images):

    snow_bytes = generate_word_doc(snow_data, root, l2, res, images)

    ppt_temp = "temp_ppt.docx"
    ppt_to_word(ppt_path, ppt_temp)

    final_doc = Document()

    snow_doc = Document(BytesIO(snow_bytes))
    for p in snow_doc.paragraphs:
        final_doc.add_paragraph(p.text)

    ppt_doc = Document(ppt_temp)
    for p in ppt_doc.paragraphs:
        final_doc.add_paragraph(p.text)

    os.remove(ppt_temp)

    buffer = BytesIO()
    final_doc.save(buffer)
    buffer.seek(0)

    return buffer.getvalue()
