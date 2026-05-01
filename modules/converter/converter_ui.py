import streamlit as st
import tempfile
import os
import re
from pptx import Presentation

from modules.converter.converter import convert_ppt
from modules.converter.ppt_metadata import extract_slide1_metadata

from modules.data.snow_loader import load_snow_data
from modules.report.domain.rca_generator import generate_rca
from modules.report.doc_generator import generate_word_doc_wrapper

from modules.common.utils.formatters import format_date
from modules.common.utils.links import get_url


# -----------------------------
# HELPERS
# -----------------------------
def clean_incident(value):
    if not value:
        return None

    match = re.search(r"INC\d{7,}", str(value))
    return match.group(0) if match else None


def extract_azure(text):
    if not text:
        return None

    match = re.search(
        r"dev\.azure\.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/(\d+)",
        str(text),
        re.IGNORECASE
    )

    return match.group(1) if match else None


def build_link(field, value):
    if not value:
        return "-"

    url = get_url(field, value)

    if not url:
        return value

    return f'<a href="{url}" target="_blank">{value}</a>'


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
        "resolved_date": format_date(
            get("closed", "vendor closed")
        ),
        "short_description": get("short description"),
        "description": get("description"),
        "work_notes": get("work notes"),
        "comments": get("additional comments"),
        "resolution": get("resolution notes"),
        "azure_bug": extract_azure(
            get("resolution notes")
        ),
        "ptc_case": get("vendor ticket")
    }


# -----------------------------
# PREVIEW TABLE
# -----------------------------
def render_preview(data):
    html = f"""
    <style>
    .tbl {{
        width:100%;
        border-collapse: collapse;
        font-family: Arial;
        font-size:14px;
        margin-bottom:20px;
    }}

    .tbl td {{
        border:1px solid black;
        padding:6px;
        vertical-align:top;
    }}

    .hdr {{
        font-weight:bold;
        background:#f2f2f2;
    }}
    </style>

    <table class="tbl">
        <tr>
            <td class="hdr">INCIDENT</td>
            <td>{build_link("incident", data.get("number"))}</td>

            <td class="hdr">CREATED BY</td>
            <td>{data.get("created_by") or "-"}</td>
        </tr>

        <tr>
            <td class="hdr">AZURE BUG</td>
            <td>{build_link("azure", data.get("azure_bug"))}</td>

            <td class="hdr">CREATED DATE</td>
            <td>{data.get("created_date") or "-"}</td>
        </tr>

        <tr>
            <td class="hdr">PTC CASE</td>
            <td>{build_link("ptc", data.get("ptc_case"))}</td>

            <td class="hdr">ASSIGNED TO</td>
            <td>{data.get("assigned_to") or "-"}</td>
        </tr>

        <tr>
            <td class="hdr">PRIORITY</td>
            <td>{data.get("priority") or "-"}</td>

            <td class="hdr">RESOLVED DATE</td>
            <td>{data.get("resolved_date") or "-"}</td>
        </tr>
    </table>

    <table class="tbl">
        <tr>
            <td class="hdr">SHORT DESCRIPTION</td>
            <td class="hdr">DESCRIPTION</td>
        </tr>

        <tr>
            <td>{data.get("short_description") or "-"}</td>
            <td>{data.get("description") or "-"}</td>
        </tr>
    </table>
    """

    st.components.v1.html(
        html,
        height=500,
        scrolling=True
    )


# -----------------------------
# MAIN UI
# -----------------------------
def render():
    st.subheader("📊 PPT Converter")

    uploaded_ppt = st.file_uploader(
        "Upload PPT",
        type=["pptx"]
    )

    if not uploaded_ppt:
        return

    with tempfile.TemporaryDirectory() as tmpdir:

        ppt_path = os.path.join(
            tmpdir,
            uploaded_ppt.name
        )

        with open(ppt_path, "wb") as f:
            f.write(uploaded_ppt.read())

        # -------------------------
        # Extract metadata
        # -------------------------
        metadata = extract_slide1_metadata(ppt_path)

        incident = clean_incident(
            metadata.get("incident")
        )

        if incident:
            st.info(f"🔍 Detected Incident: {incident}")
        else:
            st.warning(
                "Could not detect incident number from slide 1"
            )

        # -------------------------
        # Load SNOW data
        # -------------------------
        snow_data = None

        if incident:
            try:
                raw_data = load_snow_data(incident)

                if raw_data:
                    snow_data = normalize_snow_data(raw_data)
                    st.success("✅ SNOW data loaded")
                else:
                    st.warning(
                        "No SNOW data found. PPT conversion still works."
                    )

            except Exception as e:
                st.error(
                    f"SNOW loading failed: {str(e)}"
                )

        # -------------------------
        # Preview
        # -------------------------
        st.markdown("### 📄 Preview")

        if snow_data:
            render_preview(snow_data)
        else:
            st.info(
                "Preview unavailable because SNOW data not found."
            )

        # -------------------------
        # Convert PPT ONLY
        # -------------------------
        if st.button("Convert PPT"):

            with st.spinner(
                "Converting PPT to Word/PDF..."
            ):
                docx_path, pdf_path = convert_ppt(
                    ppt_path,
                    tmpdir
                )

            st.success("PPT converted successfully")

            if os.path.exists(docx_path):
                with open(docx_path, "rb") as f:
                    st.download_button(
                        "📄 Download Word",
                        f.read(),
                        file_name=os.path.basename(
                            docx_path
                        )
                    )

            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "📕 Download PDF",
                        f.read(),
                        file_name=os.path.basename(
                            pdf_path
                        )
                    )

        # -------------------------
        # Combined Report
        # -------------------------
        if st.button("Generate Combined Report"):

            if not snow_data:
                st.error(
                    "SNOW data required for combined report generation."
                )
                return

            with st.spinner(
                "Generating combined report..."
            ):
                try:
                    rca_data = generate_rca(
                        snow_data
                    )

                    output_path = os.path.join(
                        tmpdir,
                        f"{incident}_combined_report.docx"
                    )

                    generate_word_doc_wrapper(
                        snow_data=snow_data,
                        rca_data=rca_data,
                        ppt_path=ppt_path,
                        output_path=output_path
                    )

                    st.success(
                        "Combined report generated successfully"
                    )

                    with open(output_path, "rb") as f:
                        st.download_button(
                            "📥 Download Combined Report",
                            f.read(),
                            file_name=os.path.basename(
                                output_path
                            )
                        )

                except Exception as e:
                    st.error(
                        f"Combined report failed: {str(e)}"
                    )
