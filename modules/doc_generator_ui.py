import streamlit as st
from modules.doc_generator import generate_word_doc, generate_pdf

def render_doc_generator():

    st.set_page_config(layout="wide")

    # ---------------- SESSION INIT ----------------
    if "doc_data" not in st.session_state:
        st.session_state.doc_data = None

    if "bulk_data" not in st.session_state:
        st.session_state.bulk_data = ""

    if "message" not in st.session_state:
        st.session_state.message = ""

    # ---------------- SIDEBAR ----------------
    with st.sidebar:

        st.markdown("## Module")
        st.selectbox("Select Module", ["Word Report Generator"])

        st.markdown("## Filters")

        priority = st.multiselect("Priority", ["Priority 1","Priority 2","Priority 3","Priority 4"])

        date_range = st.text_input("Created Date Range")

        # APPLY FILTER
        if st.button("Apply Filters to Bulk"):
            st.session_state.bulk_data = "INC001, INC002"
            st.session_state.message = "Bulk ready"

        # ✅ CLEAR BUTTON (FULL RESET FIX)
        if st.button("Clear"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # ---------------- MAIN ----------------
    st.title("SNOW Incident Report Generator")

    incident = st.text_input("Enter Incident Number")

    bulk = st.text_area("Bulk Incident Numbers", value=st.session_state.get("bulk_data",""))

    # ---------------- BUTTON ROW (FIXED ALIGNMENT) ----------------
    col1, col2, col3, col4, col5 = st.columns(5)

    # FETCH
    with col1:
        if st.button("Fetch"):
            st.session_state.doc_data = {
                "number": incident,
                "short_description": "Edit Association button is missing from Volvo Part",
                "description": "Users need to be able to edit association on a released volvo part...",
                "priority": "Priority 4",
                "created_by": "Jordan Bingaman",
                "created_date": "2026-01-29",
                "assigned_to": "Keshavamurthy Hg",
                "resolved_date": "2026-02-16",
                "azure_bug": "695698",
                "ptc_case": "18007559"
            }
            st.session_state.message = "Incident loaded"

    # WORD
    with col2:
        if st.session_state.doc_data:
            word_bytes = generate_word_doc(st.session_state.doc_data)
            st.download_button(
                "Word",
                word_bytes,
                file_name=f"{st.session_state.doc_data['number']}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    # PDF
    with col3:
        if st.session_state.doc_data:
            pdf_bytes = generate_pdf(st.session_state.doc_data)
            st.download_button(
                "PDF",
                pdf_bytes,
                file_name=f"{st.session_state.doc_data['number']}.pdf",
                mime="application/pdf"
            )

    # BULK
    with col4:
        if st.button("Bulk"):
            st.session_state.message = "Bulk ZIP ready"

    # PREVIEW
    with col5:
        if st.button("Preview") and st.session_state.doc_data:
            d = st.session_state.doc_data
            st.markdown(f"""
            ### INCIDENT REPORT

            **Incident:** {d['number']}  
            **Priority:** {d['priority']}  

            ---
            **Short Description**  
            {d['short_description']}

            ---
            **Description**  
            {d['description']}
            """)

    # ---------------- MESSAGE (NOT STACKING) ----------------
    if st.session_state.message:
        st.success(st.session_state.message)
