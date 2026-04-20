import streamlit as st
from modules.doc_generator import generate_word_doc, generate_pdf


def render_doc_generator():

    st.set_page_config(layout="wide")

    if "doc_data" not in st.session_state:
        st.session_state.doc_data = None

    if "message" not in st.session_state:
        st.session_state.message = ""

    # SIDEBAR
    with st.sidebar:
        st.markdown("## Module")
        st.selectbox("Select Module", ["Word Report Generator"])

        st.markdown("## Filters")
        st.multiselect("Priority", ["P1","P2","P3","P4"])

        if st.button("Clear"):
            st.session_state.clear()
            st.rerun()

    # MAIN
    st.title("SNOW Incident Report Generator")

    incident = st.text_input("Enter Incident Number")

    st.markdown("### Actions")

    col1, col2, col3, col4, col5 = st.columns(5)

    # FETCH
    with col1:
        if st.button("Fetch"):
            st.session_state.doc_data = {
                "number": incident,
                "short_description": "Edit Association button missing",
                "description": "Users need to edit association...",
                "priority": "Priority 4",
                "created_by": "Jordan",
                "created_date": "2026-01-29",
                "assigned_to": "Keshava",
                "resolved_date": "2026-02-16",
                "azure_bug": "695698",
                "ptc_case": "18007559",
                "root": "",
                "l2": "",
                "res": ""
            }
            st.session_state.message = "Incident loaded"

    # WORD BUTTON (ALWAYS VISIBLE)
    with col2:
        data = st.session_state.doc_data
        st.download_button(
            "Word",
            data=generate_word_doc(data) if data else b"",
            file_name=f"{data['number']}.docx" if data else "report.docx",
            disabled=not data
        )

    # PDF BUTTON
    with col3:
        data = st.session_state.doc_data
        st.download_button(
            "PDF",
            data=generate_pdf(data) if data else b"",
            file_name=f"{data['number']}.pdf" if data else "report.pdf",
            disabled=not data
        )

    # BULK
    with col4:
        if st.button("Bulk"):
            st.session_state.message = "Bulk ready"

    # PREVIEW
    preview_clicked = col5.button("Preview")

    if preview_clicked and st.session_state.doc_data:
        d = st.session_state.doc_data

        st.markdown("---")
        st.markdown("## INCIDENT REPORT")

        st.write(f"**Incident:** {d.get('number')}")
        st.write(f"**Priority:** {d.get('priority')}")
        st.markdown("### Description")
        st.write(d.get("description"))

    # MESSAGE
    if st.session_state.message:
        st.success(st.session_state.message)
