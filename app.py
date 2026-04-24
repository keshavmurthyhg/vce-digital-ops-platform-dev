import streamlit as st
from modules.ppt_converter.converter import convert_ppt
import tempfile
import os

from modules.search.search_ui import render as search_ui
from modules.analytics.charts_page import render as analytics_ui
from modules.report.doc_generator_ui import render_doc_generator as report_ui
from modules.excel_compare.ui import render as excel_compare_ui

st.set_page_config(layout="wide")

st.sidebar.title("Navigation")

page = st.sidebar.radio("Go to", ["Home", "Search", "Analytics", "Report", "Excel Compare"])

if page == "Home":
    st.title("🏠 Home")
    st.write("Welcome! Select a module.")

elif page == "Search":
    search_ui()

elif page == "Analytics":
    analytics_ui()

elif page == "Report":
    report_ui()

elif page == "Excel Compare":
    excel_compare_ui()
elif page == "Converer":
    st.subheader("📊 PPT to Word & PDF Converter")

    uploaded_ppt = st.file_uploader(
        "Upload PowerPoint file",
        type=["pptx"]
    )
    
    if uploaded_ppt:
        st.success(f"Uploaded: {uploaded_ppt.name}")
    
        if st.button("🚀 Convert PPT"):
            with st.spinner("Converting..."):
                with tempfile.TemporaryDirectory() as tmpdir:
    
                    ppt_path = os.path.join(tmpdir, uploaded_ppt.name)
    
                    # Save uploaded file
                    with open(ppt_path, "wb") as f:
                        f.write(uploaded_ppt.read())
    
                    # Run conversion
                    docx_path, pdf_path = convert_ppt(ppt_path, tmpdir)
    
                    # Read files
                    with open(docx_path, "rb") as f:
                        docx_bytes = f.read()
    
                    with open(pdf_path, "rb") as f:
                        pdf_bytes = f.read()
    
                    st.success("✅ Conversion completed!")
    
                    col1, col2 = st.columns(2)
    
                    with col1:
                        st.download_button(
                            "📄 Download Word",
                            data=docx_bytes,
                            file_name="converted.docx"
                        )
    
                    with col2:
                        st.download_button(
                            "📕 Download PDF",
                            data=pdf_bytes,
                            file_name="converted.pdf"
                        )
