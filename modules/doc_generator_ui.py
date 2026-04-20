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

    incident = st.text_input("Enter Incident Number", key="incident_input")

    col1, col2, col3, col4, col5 = st.columns(5)

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
                "ptc_case": "18007559"
            }
            st.session_state.message = "Incident loaded"

    with col2:
        if st.session_state.doc_data:
            st.download_button(
                "Word",
                generate_word_doc(st.session_state.doc_data),
                file_name=f"{st.session_state.doc_data['number']}.docx"
            )

    with col3:
        if st.session_state.doc_data:
            st.download_button(
                "PDF",
                generate_pdf(st.session_state.doc_data),
                file_name=f"{st.session_state.doc_data['number']}.pdf"
            )

    with col4:
        if st.button("Bulk"):
            st.session_state.message = "Bulk ready"

    with col5:
        if st.button("Preview") and st.session_state.doc_data:
            d = st.session_state.doc_data
            st.markdown(f"""
            ### INCIDENT REPORT
            **Incident:** {d['number']}  
            **Priority:** {d['priority']}

            ---
            {d['description']}
            """)

    if st.session_state.message:
        st.success(st.session_state.message)
