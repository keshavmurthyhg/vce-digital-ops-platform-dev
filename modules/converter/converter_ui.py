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

            with open(ppt_path, "wb") as f:
                f.write(uploaded_ppt.read())

            if st.button("Convert PPT"):
                docx_path, pdf_path = convert_ppt(ppt_path, tmpdir)

                with open(docx_path, "rb") as f:
                    st.download_button("Download Word", f.read(), "converted.docx")

            st.divider()
            st.subheader("📦 Combined Report")

            if st.button("Generate Combined Report"):

                if "data" not in st.session_state:
                    st.error("Load SNOW data first")
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
                        "Download Combined",
                        combined,
                        "combined.docx"
                    )
