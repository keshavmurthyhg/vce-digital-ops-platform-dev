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
            if st.button("Generate Combined Report"):

            from pptx import Presentation
            from modules.converter.ppt_to_doc import extract_slide1_content
            from modules.report.snow_fetcher import fetch_snow_data_from_incident
        
            prs = Presentation(ppt_path)
        
            # 🔹 Extract incident from PPT
            incident, desc, date, azure = extract_slide1_content(prs.slides[0])
        
            st.info(f"🔍 Detected Incident: {incident}")
        
            # 🔹 Fetch SNOW data automatically
            snow_data = fetch_snow_data_from_incident(incident)
        
            if not snow_data:
                st.warning("⚠️ SNOW data not found, using PPT data fallback")
        
                # fallback (PPT-based)
                snow_data = {
                    "number": incident,
                    "short_description": desc[:100],
                    "description": desc,
                    "created_by": "PPT",
                    "created_date": date,
                    "assigned_to": "",
                    "priority": "",
                    "resolved_date": "",
                    "azure_bug": azure,
                    "ptc_case": ""
                }
        
            # Save into session (for compatibility)
            st.session_state["data"] = snow_data
        
            # 🔹 Generate combined report
            combined = generate_combined_report(
                ppt_path,
                snow_data,
                st.session_state.get("root", ""),
                st.session_state.get("l2", ""),
                st.session_state.get("res", ""),
                st.session_state.get("images", {})
            )
        
            st.download_button(
                "📄 Download Combined Report",
                combined,
                "combined_report.docx"
            )
