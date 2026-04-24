import streamlit as st
import tempfile
import os

from modules.converter.converter import convert_ppt
from modules.converter.combined_report import generate_combined_report

def render():
    st.subheader("📊 PPT to Word & PDF Converter")

    st.info("ℹ️ Note: PDF conversion may not work in cloud environment")

    uploaded_ppt = st.file_uploader(
        "Upload PowerPoint file",
        type=["pptx"]
    )

    if uploaded_ppt:
        st.success(f"Uploaded: {uploaded_ppt.name}")

        if st.button("🚀 Convert PPT"):
            with st.spinner("Converting..."):
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:

                        ppt_path = os.path.join(tmpdir, uploaded_ppt.name)

                        # Save uploaded file
                        with open(ppt_path, "wb") as f:
                            f.write(uploaded_ppt.read())

                        # Run conversion
                        docx_path, pdf_path = convert_ppt(ppt_path, tmpdir)

                        # Read DOCX
                        with open(docx_path, "rb") as f:
                            docx_bytes = f.read()

                        st.success("✅ Conversion completed!")

                        col1, col2 = st.columns(2)

                        # 📄 WORD DOWNLOAD
                        with col1:
                            st.download_button(
                                "📄 Download Word",
                                data=docx_bytes,
                                file_name="converted.docx"
                            )

                        st.divider()
                        
        st.subheader("📦 Combined Report")
        
        if st.button("Generate Combined Report"):
        
            if "data" not in st.session_state:
                st.error("⚠️ Load SNOW data first from Report module")
            else:
                with st.spinner("Generating combined report..."):
        
                    combined_bytes = generate_combined_report(
                        ppt_path,
                        st.session_state["data"],
                        st.session_state.get("root", ""),
                        st.session_state.get("l2", ""),
                        st.session_state.get("res", ""),
                        st.session_state.get("images", {})
                    )
        
                    st.download_button(
                        "📄 Download Combined Report",
                        combined_bytes,
                        "combined_report.docx"
                    )
                        
                        # 📕 PDF DOWNLOAD (SAFE)
                        with col2:
                            if pdf_path and os.path.exists(pdf_path):
                                with open(pdf_path, "rb") as f:
                                    pdf_bytes = f.read()

                                st.download_button(
                                    "📕 Download PDF",
                                    data=pdf_bytes,
                                    file_name="converted.pdf"
                                )
                            else:
                                st.warning("⚠️ PDF not available in this environment")

                except Exception as e:
                    st.error("❌ Conversion failed")
                    st.code(str(e))
