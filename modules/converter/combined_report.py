from docx import Document
from io import BytesIO
import os

from modules.converter.ppt_to_doc import ppt_to_word
from modules.report.doc_generator import generate_word_doc


def generate_combined_report(ppt_path, snow_data, root, l2, res, images):

    # 🔹 Generate SNOW doc
    snow_bytes = generate_word_doc(snow_data, root, l2, res, images)

    # 🔹 Generate PPT doc
    ppt_temp = "temp_ppt.docx"
    ppt_to_word(ppt_path, ppt_temp)

    final_doc = Document()

    # 🔹 Merge SNOW
    snow_doc = Document(BytesIO(snow_bytes))
    for el in snow_doc.element.body:
        final_doc.element.body.append(el)

    # 🔹 Merge PPT
    ppt_doc = Document(ppt_temp)
    for el in ppt_doc.element.body:
        final_doc.element.body.append(el)

    os.remove(ppt_temp)

    buffer = BytesIO()
    final_doc.save(buffer)
    buffer.seek(0)

    return buffer.getvalue()
