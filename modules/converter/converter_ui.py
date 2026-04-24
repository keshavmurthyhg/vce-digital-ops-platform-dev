import streamlit as st
import tempfile
import os

from modules.converter.converter import convert_ppt
from modules.converter.combined_report import generate_combined_report


def render():
    st.subheader("📊 PPT Converter")

    uploaded_ppt = st.file_uploader("Upload PPT", type=["pptx"])

    if uploaded_ppt:

        with tempfile.TemporaryDirectory() as tmpdir:

            ppt_path = os.path.join(tmpdir, uploaded_ppt.name)

            # Save file
            with open(ppt_path, "wb") as f:
                f.write(uploaded_ppt.read())

            # ---------------- CONVERT ---------------- #
            if st.button("Convert PPT"):

                docx_path, pdf_path = convert_ppt(ppt_path, tmpdir)

                with open(docx_path, "rb") as f:
                    st.download_button(
                        "📄 Download Word",
                        f.read(),
                        "converted.docx"
                    )

                if pdf_path and os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            "📕 Download PDF",
                            f.read(),
                            "converted.pdf"
                        )
                else:
                    st.warning("⚠️ PDF not available")

            # ---------------- COMBINED ---------------- #
            st.divider()
            st.subheader("📦 Combined Report")

            if st.button("Generate Combined Report"):

                # ❗ If SNOW data NOT available
                if "data" not in st.session_state:

                    st.warning("⚠️ SNOW data not found. Generating PPT-only report...")

                    from modules.converter.ppt_to_doc import ppt_to_word

                    temp_doc = os.path.join(tmpdir, "ppt_only.docx")
                    ppt_to_word(ppt_path, temp_doc)

                    with open(temp_doc, "rb") as f:
                        st.download_button(
                            "📄 Download PPT Report",
                            f.read(),
                            "ppt_report.docx"
                        )

                # ✅ If SNOW data available
                else:
                    combined = generate_combined_report(
                        ppt_path,
                        st.session_state["data"],
                        st.session_state.get("root", ""),
                        st.session_state.get("l2", ""),
                        st.session_state.get("res", ""),
                        st.session_state.get("images", {})
                    )

                    st.download_button(
                        "📄 Download Combined Report",
                        combined,
                        "combined.docx"
                    )
