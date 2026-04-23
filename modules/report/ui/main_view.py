import streamlit as st

from modules.report.utils.links import make_ui_link
from modules.report.doc_generator import generate_pdf, generate_word_doc
from modules.report.bulk_generator import build_bulk_reports, generate_bulk_zip
from modules.report.builders.analysis_builder import (
    build_root_cause,
    build_l2_analysis,
    build_resolution,
    merge_with_user_input
)

from modules.report.utils.utils import clean_nan, format_date, format_description, extract_azure_id


# ---------------- HELPER ---------------- #

def get_incident(df, inc):
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

    # ---------------- INIT STATE ---------------- #
    for key in ["root", "l2", "res", "images"]:
        if key not in st.session_state:
            st.session_state[key] = "" if key != "images" else {"root": [], "l2": [], "res": []}

    # ---------------- INCIDENT SELECT ---------------- #
    col1, col2, col3 = st.columns([3, 1, 4])

    with col1:
        incident = st.selectbox(
            "Select Incident",
            df["number"].dropna().unique()
        )

    with col2:
        st.write("")
        st.write("")
        fetch = st.button("Fetch", use_container_width=True)

    msg = st.empty()

    # ---------------- FETCH ---------------- #
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

    # ---------------- BULK ---------------- #
    st.markdown("### Bulk Incident Numbers")
    bulk_input = st.text_area("Enter comma-separated incident numbers")

    col1, col2, col3 = st.columns(3)

    preview_btn = col1.button("Preview", use_container_width=True)
    bulk_btn = col2.button("Bulk Generate", use_container_width=True)
    clear_btn = col3.button("Clear", use_container_width=True)

    # ---------------- CLEAR ---------------- #
    if clear_btn:
        for key in ["root", "l2", "res", "images", "data"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    # ---------------- PREVIEW ---------------- #
    if preview_btn and "data" in st.session_state:
        data = st.session_state["data"]

        st.markdown("### Preview")

        st.markdown("#### Incident Details")

        t1 = [
            ["INCIDENT", data["number"], "CREATED BY", data["created_by"]],
            ["AZURE BUG", data["azure_bug"], "CREATED DATE", data["created_date"]],
            ["PTC CASE", data["ptc_case"], "ASSIGNED TO", data["assigned_to"]],
            ["PRIORITY", data["priority"], "RESOLVED DATE", data["resolved_date"]],
        ]

        for row in t1:
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"**{row[0]}**")
            c2.markdown(make_ui_link(row[0], row[1]))
            c3.markdown(f"**{row[2]}**")
            c4.markdown(make_ui_link(row[2], row[3]))

        st.markdown("#### Description")

        c1, c2 = st.columns(2)
        c1.markdown("**SHORT DESCRIPTION**")
        c1.write(data["short_description"])

        c2.markdown("**DESCRIPTION**")
        c2.write(format_description(data["description"]))

    # ---------------- EDIT ---------------- #
    st.subheader("Edit Report Details")

    st.session_state["root"] = st.text_area("PROBLEM STATEMENT & ROOT CAUSE", st.session_state.get("root", ""))
    root_imgs = st.file_uploader("Root Images", accept_multiple_files=True)

    st.session_state["l2"] = st.text_area("TECHNICAL ANALYSIS", st.session_state.get("l2", ""))
    l2_imgs = st.file_uploader("L2 Images", accept_multiple_files=True)

    st.session_state["res"] = st.text_area("RESOLUTION & RECOMMENDATION", st.session_state.get("res", ""))
    res_imgs = st.file_uploader("Resolution Images", accept_multiple_files=True)

    st.session_state["images"] = {
        "root": root_imgs or [],
        "l2": l2_imgs or [],
        "res": res_imgs or []
    }

    # ---------------- BULK ZIP ---------------- #
    if bulk_btn:
        ids = [x.strip() for x in bulk_input.split(",") if x.strip()]

        if not ids:
            st.warning("Enter incident numbers")
        else:
            reports = build_bulk_reports(df, ids)
            zip_bytes = generate_bulk_zip(reports)

            st.download_button(
                "⬇ Download Bulk ZIP",
                data=zip_bytes,
                file_name="Bulk_Report.zip",
                mime="application/zip"
            )
