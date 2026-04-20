import streamlit as st
from modules.doc_generator import generate_word_doc, generate_pdf

st.title("SNOW Incident Report Generator")

# Inputs
incident = st.text_input("Enter Incident Number")
bulk = st.text_area("Bulk Incident Numbers")

root = st.text_area("Root Cause")
l2 = st.text_area("L2 Analysis")
res = st.text_area("Resolution")

# Images
root_img = st.file_uploader("Root Image")
l2_img = st.file_uploader("L2 Image")
res_img = st.file_uploader("Resolution Image")

images = {"root": root_img, "l2": l2_img, "res": res_img}

# Buttons row
col1, col2, col3, col4, col5 = st.columns(5)

# Fetch
with col1:
    if st.button("Fetch"):
        st.session_state["doc_data"] = {
            "number": incident,
            "azure_bug": "695698",
            "ptc_case": "18007559",
            "priority": "Priority 4",
            "created_by": "Jordan Bingaman",
            "created_date": "2026-01-29",
            "assigned_to": "Keshavamurthy Hg",
            "resolved_date": "2026-02-16",
            "short_description": "Sample",
            "description": "Sample Desc"
        }
        st.session_state["msg"] = "Incident loaded"

# Word
with col2:
    if st.button("Word"):
        st.session_state["word"] = generate_word_doc(
            st.session_state["doc_data"], root, l2, res, images
        )
        st.session_state["msg"] = "Word generated"

    if "word" in st.session_state:
        st.download_button("⬇", st.session_state["word"], f"{incident}.docx")

# PDF
with col3:
    if st.button("PDF"):
        st.session_state["pdf"] = generate_pdf(
            st.session_state["doc_data"], root, l2, res, images
        )
        st.session_state["msg"] = "PDF generated"

    if "pdf" in st.session_state:
        st.download_button("⬇", st.session_state["pdf"], f"{incident}.pdf")

# Bulk
with col4:
    if st.button("Bulk"):
        st.session_state["msg"] = "Bulk ready"

# Preview
with col5:
    if st.button("Preview"):
        st.write(st.session_state.get("doc_data"))

# Message (single, not stacked)
if "msg" in st.session_state:
    st.success(st.session_state["msg"])

# Clear
if st.button("Clear"):
    st.session_state.clear()
    st.rerun()
