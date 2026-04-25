import streamlit as st
import tempfile
import os
import re

from modules.report.builders.analysis_builder import build_report_sections
from modules.converter.converter import convert_ppt
from modules.report.utils.utils import format_date


# ---------------- NORMALIZER ---------------- #
def normalize_snow_data(data):
    if not data:
        return {}

    def get(*keys):
        for k in keys:
            if k in data and data[k]:
                return data[k]
        return None

    return {
        "number": get("number"),

        # ✅ FIXED MAPPING BASED ON YOUR DATA
        "created_by": get("opened by"),
        "created_date": get("created"),

        "assigned_to": get("assigned to"),

        "priority": get("priority"),

        "resolved_date": get("resolved"),

        "short_description": get("short description"),
        "description": get("description") or "",

        # ✅ IMPORTANT TEXT FIELDS
        "work_notes": get("work notes"),
        "comments": get("additional comments"),
        "resolution": get("resolution notes"),

        # ✅ LINKS
        "azure_bug": extract_azure_id(get("resolution notes") or ""),
        "ptc_case": get("vendor ticket"),
    }

def clean_incident(incident):
    if not incident:
        return None
    match = re.search(r'INC\d{7,}', str(incident))
    return match.group(0) if match else None


# ---------------- UI ---------------- #
def render():
    st.subheader("📊 PPT Converter")

    uploaded_ppt = st.file_uploader("Upload PPT", type=["pptx"])

    if uploaded_ppt:

        with tempfile.TemporaryDirectory() as tmpdir:

            ppt_path = os.path.join(tmpdir, uploaded_ppt.name)

            with open(ppt_path, "wb") as f:
                f.write(uploaded_ppt.read())

            # -------- CONVERT -------- #
            if st.button("Convert PPT"):

                docx_path, pdf_path = convert_ppt(ppt_path, tmpdir)

                with open(docx_path, "rb") as f:
                    st.download_button("📄 Download Word", f.read(), "converted.docx")

                if pdf_path and os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        st.download_button("📕 Download PDF", f.read(), "converted.pdf")
                else:
                    st.warning("⚠️ PDF not available")

            # -------- COMBINED -------- #
            if st.button("Generate Combined Report"):

                from pptx import Presentation
                from modules.converter.ppt_to_doc import extract_slide1_content
                from modules.data.snow_loader import load_snow_data
                from modules.converter.ppt_extractor import extract_ppt_content
                from modules.report.doc_generator import generate_word_doc_wrapper

                prs = Presentation(ppt_path)

                # Extract
                incident, desc, date, azure = extract_slide1_content(prs.slides[0])
                incident = clean_incident(incident)

                st.info(f"🔍 Detected Incident: {incident}")

                
                # Fetch SNOW
                df = load_snow_data()

                if df is None or df.empty:
                    st.error("❌ Failed to load SNOW data")
                    return
                
                # 🔍 Filter by incident
                row = df[df["number"] == incident]
                
                if row.empty:
                    st.error("❌ Incident not found in SNOW")
                    return
                
                st.success("✅ SNOW data loaded")
                
                # ✅ Convert row → dict (CRITICAL)
                
                raw_data = row.iloc[0].to_dict()
                snow_data = normalize_snow_data(raw_data)
                st.write("DEBUG ROW:", raw_data)
                # Build sections
                root, l2, res = build_report_sections(snow_data)

                # PPT data
                ppt_data = extract_ppt_content(ppt_path, tmpdir)

                # Generate
                doc_bytes = generate_word_doc_wrapper(
                    snow_data,
                    root,
                    l2,
                    res,
                    {},
                    ppt_data=ppt_data
                )

                st.subheader("📄 Preview")

                # -------- TABLE 1 -------- #
                st.markdown("### Incident Details")
                
                t1 = [
                    ["INCIDENT", snow_data.get("number"), "CREATED BY", snow_data.get("created_by")],
                    ["AZURE BUG", snow_data.get("azure_bug"), "CREATED DATE", format_date(snow_data.get("created_date"))],
                    ["PTC CASE", snow_data.get("ptc_case"), "ASSIGNED TO", snow_data.get("assigned_to")],
                    ["PRIORITY", snow_data.get("priority"), "RESOLVED DATE", format_date(snow_data.get("resolved_date"))],
                ]
                
                for row in t1:
                    col1, col2, col3, col4 = st.columns(4)
                
                    with col1:
                        st.markdown(f"**{row[0]}**")
                
                    with col2:
                        st.markdown(make_ui_link(row[0], row[1]))
                
                    with col3:
                        st.markdown(f"**{row[2]}**")
                
                    with col4:
                        st.markdown(make_ui_link(row[2], row[3]))
                
                # -------- TABLE 2 -------- #
                st.markdown("---")
                st.markdown("### Description")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**SHORT DESCRIPTION**")
                    st.write(snow_data.get("short_description") or "-")
                
                with col2:
                    st.markdown("**DESCRIPTION**")
                    st.write(snow_data.get("description") or "-")
                
                st.download_button(
                    "📄 Download Combined Report",
                    doc_bytes,
                    "combined_report.docx"
                )
