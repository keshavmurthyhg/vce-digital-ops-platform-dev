import os
from modules.converter.ppt_to_doc import ppt_to_word
from modules.converter.doc_to_pdf import doc_to_pdf


def convert_ppt(ppt_path, output_folder):
    base = os.path.splitext(os.path.basename(ppt_path))[0]

    docx_path = os.path.join(output_folder, f"{base}.docx")

    ppt_to_word(ppt_path, docx_path)

    pdf_path = None

    try:
        doc_to_pdf(docx_path, output_folder)
        pdf_path = os.path.join(output_folder, f"{base}.pdf")
    except:
        pass

    return docx_path, pdf_path
