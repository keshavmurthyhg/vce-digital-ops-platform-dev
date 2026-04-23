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
from modules.report.utils import format_date


# ---------------- HELPER ---------------- #

def get_incident(df, inc):
    df["number"] = df["number"].astype(str).str.upper()
    row = df[df["number"] == inc.upper()]

    if row.empty:
        return None

    r = row.iloc[0]

    resolution_text = (
        r.get("RESOLUTION & RECOMMENDATION notes")
        or r.get("resolution notes")
        or r.get("Resolution Notes")
        or ""
    )

    return {
        "number": r.get("number"),
        "short_description": r.get("short description"),
        "description": r.get("description"),
        "priority": r.get("priority"),
        "created_by": r.get("caller"),
        "created_date": str(r.get("created")).split()[0],
        "assigned_to": r.get("assigned to"),
        "resolved_date": str(r.get("resolved")).split()[0],
        "work_notes": r.get("work notes", ""),
        "comments": r.get("additional comments", ""),
        "resolution": resolution_text,
        "azure_bug": r.get("azure bug"),
        "ptc_case": r.get("vendor ticket"),
    }


# ---------------- MAIN UI ---------------- #

def render_main(df):

    st.title("Incident Report Generator")

    # ---------------- INIT STATE ---------------- #
    for key in ["root", "l2", "res", "images"]:
        if key not in st.session_state:
            st.session_state[key] = "" if key != "images" else {"root": [], "l2": [], "res": []}

    # ---------------- INCIDENT SELECT ---------------- #
    col1, col2 = st.columns([4, 1])

    with col1:
        incident = st.selectbox(
            "Select Incident",
            df["number"].dropna().unique()
        )

    with col2:
        st.write("")
        fetch = st.button("Fetch", use_container_width=True)

    # ---------------- FETCH LOGIC ---------------- #
    if fetch:
        data = get_incident(df, incident)

        if data:
            st.session_state["data"] = data

            auto_root = build_root_cause(data["work_notes"])
            auto_l2 = build_l2_analysis(data["comments"])
            auto_res = build_resolution(data["resolution"])

            st.session_state["root"] = merge_with_user_input(
                auto_root, st.session_state.get("root")
            )
            st.session_state["l2"] = merge_with_user_input(
                auto_l2, st.session_state.get("l2")
            )
            st.session_state["res"] = merge_with_user_input(
                auto_res, st.session_state.get("res")
            )

            st.success(f"Loaded {incident}")
        else:
            st.error("Incident not found")

    # ---------------- BULK INPUT ---------------- #
    st.markdown("### Bulk Incident Numbers")

    bulk_input = st.text_area(
        "Enter comma-separated incident numbers",
        value=st.session_state.get("bulk_ids", ""),
        key="bulk_ids"
    )

    # ---------------- ACTION BUTTONS ---------------- #
    colA, colB, colC, colD = st.columns(4)

    with colA:
        generate_pdf_btn = st.button("Generate PDF", use_container_width=True)

    with colB:
        generate_word_btn = st.button("Generate Word", use_container_width=True)

    with colC:
        bulk_btn = st.button("Bulk Generate", use_container_width=True)

    with colD:
        clear_btn = st.button("Clear", use_container_width=True)

    # ---------------- CLEAR ---------------- #
    if clear_btn:
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

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
