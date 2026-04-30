import streamlit as st
import tempfile
import os
import re

from modules.report.domain.rca_generator import generate_rca
from modules.converter.converter import convert_ppt
from modules.common.utils.formatters import format_date
from modules.data.snow_loader import load_snow_data
from modules.converter.ppt_extractor import extract_ppt_content
from modules.report.doc_generator import generate_word_doc_wrapper
from pptx import Presentation
from modules.converter.ppt_to_doc import extract_slide1_content


# ---------------- AZURE BUG ---------------- #
def extract_azure(text):
    if not text:
        return None

    text = str(text)

    match = re.search(
        r"dev\.azure\.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/(\d{6})",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1)

    return None


# ---------------- NORMALIZER ---------------- #
def normalize_snow_data(data):
    def get(*keys):
        for k in keys:
            if k in data and data[k]:
                return data[k]
        return None

    return {
        "number": get("number"),
        "created_by": get("opened by"),
        "created_date": format_date(get("created")),
        "assigned_to": get("assigned to"),
        "priority": get("priority"),
        "resolved_date": format_date(get("closed", "vendor closed")),
        "short_description": get("short description"),
        "description": get("description") or "",
        "work_notes": get("work notes"),
        "comments": get("additional comments"),
        "resolution": get("resolution notes"),
        "azure_bug": extract_azure(get("resolution notes")),
        "ptc_case": get("vendor ticket"),
    }


# ---------------- CLEAN INCIDENT ---------------- #
def clean_incident(val):
    if not val:
        return None
    m = re.search(r'INC\d{7,}', str(val))
    return m.group(0) if m else None


# ---------------- LINK BUILDER ---------------- #
def link(val, type_):
    if not val:
        return "-"

    if type_ == "incident":
        return f'<a href="https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={val}" target="_blank">{val}</a>'

    if type_ == "azure":
        return f'<a href="https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{val}" target="_blank">{val}</a>'

    if type_ == "ptc":
        return f'<a href="https://support.ptc.com/appserver/cs/view/case.jsp?n={val}" target="_blank">{val}</a>'

    return val


# ---------------- TABLE PREVIEW ---------------- #
def render_preview_table(data):

    html = f"""
    <style>
    .tbl {{
        width: 100%;
        border-collapse: collapse;
        font-family: Arial;
        font-size: 14px;
        margin-bottom: 20px;
    }}
    .tbl td {{
        border: 1px solid black;
        padding: 6px;
    }}
    .hdr {{
        font-weight: bold;
        background: #f2f2f2;
    }}
    </style>

    <table class="tbl">
        <tr>
            <td class="hdr">INCIDENT</td>
            <td>{link(data["number"], "incident")}</td>
            <td class="hdr">CREATED BY</td>
            <td>{data["created_by"] or "-"}</td>
        </tr>
        <tr>
            <td class="hdr">AZURE BUG</td>
            <td>{link(data["azure_bug"], "azure")}</td>
            <td class="hdr">CREATED DATE</td>
            <td>{data["created_date"] or "-"}</td>
        </tr>
        <tr>
            <td class="hdr">PTC CASE</td>
            <td>{link(data["ptc_case"], "ptc")}</td>
            <td class="hdr">ASSIGNED TO</td>
            <td>{data["assigned_to"] or "-"}</td>
        </tr>
        <tr>
            <td class="hdr">PRIORITY</td>
            <td>{data["priority"] or "-"}</td>
            <td class="hdr">RESOLVED DATE</td>
            <td>{data["resolved_date"] or "-"}</td>
        </tr>
    </table>
    """

    #st.markdown(html, unsafe_allow_html=True)#
    st.components.v1.html(html, height=250, scrolling=True)


def render_description_table(data):

    html = f"""
    <table class="tbl">
        <tr>
            <td class="hdr">SHORT DESCRIPTION</td>
            <td class="hdr">DESCRIPTION</td>
        </tr>
        <tr>
            <td>{data["short_description"] or "-"}</td>
            <td>{data["description"] or "-"}</td>
        </tr>
    </table>
    """

    st.markdown(html, unsafe_allow_html=True)


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

                prs = Presentation(ppt_path)
                incident, desc, date, azure = extract_slide1_content(prs.slides[0])
                incident = clean_incident(incident)

                st.info(f"🔍 Detected Incident: {incident}")

                df = load_snow_data()

                if df is None or df.empty:
                    st.error("❌ Failed to load SNOW data")
                    return

                row = df[df["number"] == incident]

                if row.empty:
                    st.error("❌ Incident not found in SNOW")
                    return

                st.success("✅ SNOW data loaded")

                raw_data = row.iloc[0].to_dict()
                snow_data = normalize_snow_data(raw_data)

                # Build sections
                rca = generate_rca(snow_data)

                root = rca["problem"]
                l2 = rca["analysis"]
                res = rca["resolution"]

                # PPT content (UNCHANGED)
                ppt_data = extract_ppt_content(ppt_path, tmpdir)

                # Generate Word
                doc_bytes = generate_word_doc_wrapper(
                    snow_data,
                    root,
                    l2,
                    res,
                    {},
                    ppt_data=ppt_data
                )

                # -------- PREVIEW -------- #
                st.subheader("📄 Preview")

                render_preview_table(snow_data)
                render_description_table(snow_data)

                st.download_button(
                    "📄 Download Combined Report",
                    doc_bytes,
                    "combined_report.docx"
                )
