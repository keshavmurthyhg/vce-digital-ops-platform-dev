import streamlit as st

from modules.report.renderers.pdf_renderer import generate_pdf_doc
from modules.report.renderers.word_renderer import generate_word_doc
from modules.common.utils.text_cleaner import format_description
from modules.common.utils.links import extract_azure_id
from modules.report.domain.rca_generator import generate_rca

def enrich_data(data):
    print("===== DEBUG AZURE EXTRACTION =====")

    print("resolution_notes:", data.get("resolution_notes"))
    print("work_notes:", data.get("work_notes"))
    print("comments:", data.get("comments"))
    print("additional_comments:", data.get("additional_comments"))
    
    notes = " ".join([
        str(data.get("resolution_notes", "")),
        str(data.get("work_notes", "")),
        str(data.get("comments", "")),
        str(data.get("additional_comments", ""))
    ])
    
    
    if not data.get("azure_bug") or str(data.get("azure_bug")).strip() == "":
        data["azure_bug"] = extract_azure_id(notes)

    return data

def prepare_data(data):
    """
    Central place for all sanitization & formatting
    """
    data = enrich_data(data)
    safe_data = data.copy()

    # ✅ DEBUG INSIDE FUNCTION
    #st.write("DEBUG BEFORE RCA:", data.get("short_description"))#

    safe_data["description"] = format_description(data.get("description"))

    # ✅ RCA
    rca = generate_rca(data)

    safe_data["problem"] = rca["problem"]

    # ✅ DEBUG AFTER
    #st.write("DEBUG AFTER RCA:", safe_data.get("problem"))#

    safe_data["analysis"] = rca["analysis"]
    safe_data["resolution"] = rca["resolution"]

    return safe_data

def safe_images(images):
    if not isinstance(images, dict):
        return {"root": [], "l2": [], "res": []}
    return images

if actions.get("pdf"):
    if "data" not in st.session_state:
        st.warning("Please fetch an incident first")
    else:
        from modules.report.doc_generator import generate_pdf

        pdf_bytes = generate_pdf(
            data=st.session_state["data"],
            root=st.session_state.get("problem"),
            l2=st.session_state.get("root_cause"),
            res=st.session_state.get("resolution"),
            images=None
        )

        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name="incident_report.pdf",
            mime="application/pdf"
        )

if actions.get("word"):
    if "data" not in st.session_state:
        st.warning("Please fetch an incident first")
    else:
        from modules.report.doc_generator import generate_word_doc_wrapper

        word_bytes = generate_word_doc_wrapper(
            data=st.session_state["data"],
            root=st.session_state.get("problem"),
            l2=st.session_state.get("root_cause"),
            res=st.session_state.get("resolution"),
            images=None
        )

        st.download_button(
            label="Download Word",
            data=word_bytes,
            file_name="incident_report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

