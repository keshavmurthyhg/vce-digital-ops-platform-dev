from docx import Document
from io import BytesIO
import os

from modules.converter.ppt_to_doc import ppt_to_word
from modules.report.doc_generator import generate_word_doc


def append_doc(source_doc, target_doc):
    """
    Append full content (tables + paragraphs) properly
    """
    for element in source_doc.element.body:
        target_doc.element.body.append(element)


def generate_combined_report(ppt_path, snow_data, root, l2, res, images):

    # 🔹 Step 1: Generate SNOW doc (already structured with tables)
    snow_bytes = generate_word_doc(snow_data, root, l2, res, images)
    snow_doc = Document(BytesIO(snow_bytes))

    # 🔹 Step 2: Generate PPT doc
    ppt_temp = "temp_ppt.docx"
    ppt_to_word(ppt_path, ppt_temp)
    ppt_doc = Document(ppt_temp)

    # 🔹 Step 3: Create final doc
    final_doc = Document()

    # ✅ CRITICAL: copy full structure, not text
    append_doc(snow_doc, final_doc)

    # Optional: page break between sections
    final_doc.add_page_break()

    append_doc(ppt_doc, final_doc)

    os.remove(ppt_temp)

    # 🔹 Save
    buffer = BytesIO()
    final_doc.save(buffer)
    buffer.seek(0)

    return buffer.getvalue()
