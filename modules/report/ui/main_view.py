import streamlit as st
from io import BytesIO
import zipfile

from modules.report.doc_generator import generate_pdf, generate_word_doc
from modules.report.bulk_generator import build_bulk_reports, generate_bulk_zip
from modules.report.builders.analysis_builder import (
    build_root_cause,
    build_l2_analysis,
    build_resolution,
    merge_with_user_input
)
from modules.report.utils import clean_nan, format_date, format_description


# ---------------- HELPER ---------------- #

def get_incident(df, inc):
    row = df[df["number"].astype(str).str.upper() == inc.upper()]
    if row.empty:
        return None
    r = row.iloc[0]

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
        "resolution": r.get("resolution notes", ""),
        "azure_bug": clean_nan(r.get("azure bug")),
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
    col1, col2 = st.columns([6,1])

    with col1:
        incident = st.selectbox("Select Incident", df["number"].dropna().unique())

    with col2:
        st.write(""); st.write("")
        fetch = st.button("Fetch", use_container_width=True)

    
    # ---------------- FETCH LOGIC ---------------- #
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

            st.success("Loaded")
        else:
            st.error("Not found")

    # ---------------- BULK INPUT ---------------- #
    st.markdown("### Bulk Incident Numbers")
    bulk_input = st.text_area("Enter comma-separated incident numbers", key="bulk_ids")

    # ---------------- ACTION BUTTONS ---------------- #
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

    # ---------------- CLEAR ---------------- #
    if clear_btn:
        st.session_state.clear()
        st.rerun()

     # ---------------- PREVIEW ---------------- #
    
    if preview_btn and "data" in st.session_state:
        data = st.session_state["data"]
    
        st.markdown("### Preview")
    
        # -------- TABLE 1 -------- #
        t1 = [
            ["INCIDENT", data["number"], "CREATED BY", data["created_by"]],
            ["AZURE BUG", data["azure_bug"], "CREATED DATE", data["created_date"]],
            ["PTC CASE", data["ptc_case"], "ASSIGNED TO", data["assigned_to"]],
            ["PRIORITY", data["priority"], "RESOLVED DATE", data["resolved_date"]],
        ]
    
        st.table(t1)
    
        # -------- TABLE 2 -------- #
        t2 = [
            ["SHORT DESCRIPTION", "DESCRIPTION"],
            [data["short_description"], format_description(data["description"])]
        ]
    
        st.table(t2)
    
    # ---------------- EDITABLE BLOCKS ---------------- #
    st.subheader("Edit Report Details")

    st.session_state["root"] = st.text_area(
        "PROBLEM STATEMENT & ROOT CAUSE",
        value=st.session_state.get("root", ""),
        height=150
    )

    root_imgs = st.file_uploader(
        "Root Images",
        accept_multiple_files=True,
        key="root_img"
    )

    st.session_state["l2"] = st.text_area(
        "TECHNICAL ANALYSIS",
        value=st.session_state.get("l2", ""),
        height=150
    )

    l2_imgs = st.file_uploader(
        "L2 Images",
        accept_multiple_files=True,
        key="l2_img"
    )

    st.session_state["res"] = st.text_area(
        "RESOLUTION & RECOMMENDATION",
        value=st.session_state.get("res", ""),
        height=150
    )

    res_imgs = st.file_uploader(
        "Resolution Images",
        accept_multiple_files=True,
        key="res_img"
    )

    st.session_state["images"] = {
        "root": root_imgs or [],
        "l2": l2_imgs or [],
        "res": res_imgs or []
    }

    # ---------------- PDF DOWNLOAD ---------------- #
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

            st.download_button(
                "⬇ Download PDF",
                data=pdf_bytes,
                file_name=f"{data['number']}.pdf",
                mime="application/pdf"
            )

    # ---------------- WORD DOWNLOAD ---------------- #
    if generate_word_btn:
        if "data" not in st.session_state:
            st.warning("Fetch incident first")
        else:
            data = st.session_state["data"]

            word_bytes = generate_word_doc(
                data,
                st.session_state.get("root"),
                st.session_state.get("l2"),
                st.session_state.get("res"),
                st.session_state.get("images")
            )

            st.download_button(
                "⬇ Download Word",
                data=word_bytes,
                file_name=f"{data['number']}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    # ---------------- BULK GENERATE ---------------- #
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
                file_name=f"Bulk_Report_{format_date('2026-01-01')}.zip",
                mime="application/zip"
            )
