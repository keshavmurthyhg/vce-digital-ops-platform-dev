import streamlit as st
import tempfile
import os
import re

from modules.report.builders.analysis_builder import build_report_sections
from modules.converter.converter import convert_ppt


def clean_incident(incident):
    if not incident:
        return None

    match = re.search(r'INC\d{7,}', str(incident))
    return match.group(0) if match else None


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
                    st.download_button("📄 Download Word", f.read(), "converted.docx")

                if pdf_path and os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        st.download_button("📕 Download PDF", f.read(), "converted.pdf")
                else:
                    st.warning("⚠️ PDF not available")

            # ---------------- COMBINED ---------------- #
            if st.button("Generate Combined Report"):

                from pptx import Presentation
                from modules.converter.ppt_to_doc import extract_slide1_content
                from modules.data.snow_fetcher import fetch_snow_data_from_incident
                from modules.converter.ppt_extractor import extract_ppt_content
                from modules.report.doc_generator import generate_word_doc_wrapper

                prs = Presentation(ppt_path)

                # 🔹 Extract incident
                incident, desc, date, azure = extract_slide1_content(prs.slides[0])
                incident = clean_incident(incident)

                st.info(f"🔍 Detected Incident: {incident}")

                # 🔹 Fetch SNOW
                snow_data = fetch_snow_data_from_incident(incident)

                if snow_data:
                    st.success("✅ SNOW data loaded")
                else:
                    st.warning("⚠️ SNOW not found — using PPT fallback")

                    snow_data = {
                        "number": incident,
                        "short_description": desc.split("\n")[0] if desc else "",
                        "description": desc,
                        "created_by": "PPT",
                        "created_date": date,
                        "assigned_to": "",
                        "priority": "",
                        "resolved_date": "",
                        "azure_bug": azure,
                        "ptc_case": ""
                    }

                # 🔥 CRITICAL FIX — BUILD REPORT SECTIONS
                root, l2, res = build_report_sections(snow_data)

                # 🔹 Extract PPT content
                ppt_data = extract_ppt_content(ppt_path, tmpdir)

                # 🔹 Generate document
                doc_bytes = generate_word_doc_wrapper(
                    snow_data,
                    root,
                    l2,
                    res,
                    {},  # images
                    ppt_data=ppt_data
                )

                st.download_button(
                    "📄 Download Combined Report",
                    doc_bytes,
                    "combined_report.docx"
                )
