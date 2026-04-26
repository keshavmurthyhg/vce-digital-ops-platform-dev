import streamlit as st
from io import BytesIO
import zipfile

from modules.report.utils.links import make_ui_link
from modules.report.doc_generator import generate_pdf, generate_word_doc_wrapper
from modules.report.bulk_generator import build_bulk_reports, generate_bulk_zip
from modules.report.builders.analysis_builder import (
    build_root_cause,
    build_l2_analysis,
    build_resolution,
    merge_with_user_input
)

from modules.report.utils.utils import clean_nan, format_date, format_description
from modules.report.utils.utils import extract_azure_id


# ---------------- PREVIEW TABLES ---------------- #

def render_preview_table(data):
    def val(x):
        return x if x else "-"

    def link(label, value):
        return make_ui_link(label, value) if value else "-"

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
        vertical-align: middle;
    }}
    .hdr {{
        font-weight: bold;
        background: #f2f2f2;
    }}
    </style>

    <table class="tbl">
        <tr>
            <td class="hdr">INCIDENT</td>
            <td>{link("incident", data.get("number"))}</td>
            <td class="hdr">CREATED BY</td>
            <td>{val(data.get("created_by"))}</td>
        </tr>
        <tr>
            <td class="hdr">AZURE BUG</td>
            <td>{link("azure bug", data.get("azure_bug"))}</td>
            <td class="hdr">CREATED DATE</td>
            <td>{val(data.get("created_date"))}</td>
        </tr>
        <tr>
            <td class="hdr">PTC CASE</td>
            <td>{link("ptc case", data.get("ptc_case"))}</td>
            <td class="hdr">ASSIGNED TO</td>
            <td>{val(data.get("assigned_to"))}</td>
        </tr>
        <tr>
            <td class="hdr">PRIORITY</td>
            <td>{val(data.get("priority"))}</td>
            <td class="hdr">RESOLVED DATE</td>
            <td>{val(data.get("resolved_date"))}</td>
        </tr>
    </table>
    """

    st.markdown(html, unsafe_allow_html=True)


def render_description_table(data):
    def val(x):
        return x if x else "-"

    html = f"""
    <table class="tbl">
        <tr>
            <td class="hdr">SHORT DESCRIPTION</td>
            <td class="hdr">DESCRIPTION</td>
        </tr>
        <tr>
            <td>{val(data.get("short_description"))}</td>
            <td>{val(data.get("description"))}</td>
        </tr>
    </table>
    """

    st.markdown(html, unsafe_allow_html=True)


# ---------------- HELPER ---------------- #

def get_incident(df, inc):
    incident_col = "number" if "number" in df.columns else df.columns[0]
    row = df[df["number"].astype(str).str.upper() == inc.upper()]
    if row.empty:
        return None

    r = row.iloc[0]

    resolution_text = r.get("resolution notes", "")
    azure_id = extract_azure_id(resolution_text)

    return {
        "number": clean_nan(r.get("number")),
        "short_description": clean_nan(r.get("short description")),
        "description": clean_nan(r.get("description")),
        "priority": clean_nan(r.get("priority")),
        "created_by": clean_nan(r.get("caller")),
        "created_date": format_date(r.get("created")),
        "assigned_to": clean_nan(r.get("assigned to")),
        "resolved_date": format_date(r.get("resolved")),

        "work_notes": r.get("work notes", ""),
        "comments": r.get("additional comments", ""),
        "resolution": resolution_text,

        "azure_bug": azure_id if azure_id else clean_nan(r.get("azure bug")),
        "ptc_case": clean_nan(r.get("vendor ticket")),
    }


# ---------------- MAIN UI ---------------- #

def render_main(df):
    st.title("Incident Report Generator")

    # INIT STATE
    for key in ["root", "l2", "res", "images"]:
        if key not in st.session_state:
            st.session_state[key] = "" if key != "images" else {"root": [], "l2": [], "res": []}

    # INCIDENT SELECT
    col1, col2, col3 = st.columns([3, 1, 4])

    with col1:
        incident_col = "number" if "number" in df.columns else df.columns[0]

        incident = st.selectbox(
            "Select Incident",
            df[incident_col].dropna().astype(str).unique()
        )

    with col2:
        st.write("")
        st.write("")
        fetch = st.button("Fetch", use_container_width=True)

    msg = st.empty()

    # FETCH LOGIC
    if fetch:
        data = get_incident(df, incident)

        if data:
            st.session_state["data"] = data

            st.session_state["root"] = merge_with_user_input(
                build_root_cause(data["work_notes"]),
                st.session_state.get("root")
            )
            st.session_state["l2"] = merge_with_user_input(
                build_l2_analysis(data["comments"]),
                st.session_state.get("l2")
            )
            st.session_state["res"] = merge_with_user_input(
                build_resolution(data["resolution"]),
                st.session_state.get("res")
            )

            msg.success("Loaded")
        else:
            msg.error("Not found")

    # BULK INPUT
    st.markdown("### Bulk Incident Numbers")
    bulk_input = st.text_area("Enter comma-separated incident numbers", key="bulk_ids")

    # ACTION BUTTONS
    colA, colB, colC, colD, colE = st.columns(5)

    with colA:
        generate_pdf_btn = st.button("Generate PDF", use_container_width=True)

    with colB:
        generate_word_btn = st.button("Generate Word", use_container_width=True)

    with colC:
        bulk_btn = st.button("Bulk Generate", use_container_width=True)

    with colD:
        clear_btn = st.button("Clear", use_container_width=True)

    with colE:
        preview_btn = st.button("Preview", use_container_width=True)

    # CLEAR
    if clear_btn:
        for key in ["root", "l2", "res", "images", "data"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    # PREVIEW (UPDATED)
    if preview_btn and "data" in st.session_state:
        data = st.session_state["data"]

        st.markdown("### Preview")

        st.markdown("#### Incident Details")
        render_preview_table(data)

        st.markdown("#### Description")
        render_description_table(data)

    # EDITABLE BLOCKS
    st.subheader("Edit Report Details")

    st.session_state["root"] = st.text_area(
        "PROBLEM STATEMENT & ROOT CAUSE",
        value=st.session_state.get("root", ""),
        height=150
    )

    root_imgs = st.file_uploader("Root Images", accept_multiple_files=True, key="root_img")

    st.session_state["l2"] = st.text_area(
        "TECHNICAL ANALYSIS",
        value=st.session_state.get("l2", ""),
        height=150
    )

    l2_imgs = st.file_uploader("L2 Images", accept_multiple_files=True, key="l2_img")

    st.session_state["res"] = st.text_area(
        "RESOLUTION & RECOMMENDATION",
        value=st.session_state.get("res", ""),
        height=150
    )

    res_imgs = st.file_uploader("Resolution Images", accept_multiple_files=True, key="res_img")

    st.session_state["images"] = {
        "root": root_imgs or [],
        "l2": l2_imgs or [],
        "res": res_imgs or []
    }

    # PDF
    if generate_pdf_btn:
        if "data" not in st.session_state:
            st.warning("Fetch incident first")
        else:
            data = st.session_state["data"]

            pdf_bytes = generate_pdf(
                data,
                st.session_state.get("root"),
                st.session_state.get("l2"),
                st.session_state.get("res"),
                st.session_state.get("images")
            )

            st.download_button("Download PDF", pdf_bytes, "report.pdf")

    # WORD
    if generate_word_btn:
        if "data" not in st.session_state:
            st.warning("Fetch incident first")
        else:
            data = st.session_state["data"]

            word_bytes = generate_word_doc_wrapper(
                data,
                st.session_state.get("root"),
                st.session_state.get("l2"),
                st.session_state.get("res"),
                st.session_state.get("images")
            )

            st.download_button("Download Word", word_bytes, "report.docx")
