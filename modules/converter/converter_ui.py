import streamlit as st
import tempfile
import os

from modules.converter.converter import convert_ppt
from modules.converter.combined_report import generate_combined_report

def render():
    st.subheader("📊 PPT to Word & PDF Converter")

    uploaded_ppt = st.file_uploader("Upload PowerPoint file", type=["pptx"])

    if uploaded_ppt:

        with tempfile.TemporaryDirectory() as tmpdir:

            ppt_path = os.path.join(tmpdir, uploaded_ppt.name)

            with open(ppt_path, "wb") as f:
                f.write(uploaded_ppt.read())

            if st.button("🚀 Convert PPT"):

                docx_path, pdf_path = convert_ppt(ppt_path, tmpdir)

                with open(docx_path, "rb") as f:
                    docx_bytes = f.read()

                col1, col2 = st.columns(2)

                with col1:
                    st.download_button("📄 Word", docx_bytes, "converted.docx")

                with col2:
                    if pdf_path and os.path.exists(pdf_path):
                        with open(pdf_path, "rb") as f:
                            pdf_bytes = f.read()
                        st.download_button("📕 PDF", pdf_bytes, "converted.pdf")
                    else:
                        st.warning("PDF not available")

            # ✅ Combined report (INSIDE same block)
            st.divider()
            st.subheader("📦 Combined Report")

            if st.button("Generate Combined Report"):

                if "data" not in st.session_state:
                    st.error("Load SNOW data first")
                else:
                    combined_bytes = generate_combined_report(
                        ppt_path,
                        st.session_state["data"],
                        st.session_state.get("root", ""),
                        st.session_state.get("l2", ""),
                        st.session_state.get("res", ""),
                        st.session_state.get("images", {})
                    )

                    st.download_button(
                        "📄 Combined Report",
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
