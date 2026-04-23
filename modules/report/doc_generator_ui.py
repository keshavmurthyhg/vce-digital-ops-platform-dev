import streamlit as st
import pandas as pd
import zipfile
import re
import base64

from modules.report.snow_loader import load_snow_data
from modules.report.doc_generator import generate_word_doc, generate_pdf
from io import BytesIO
from datetime import datetime

from modules.report.analysis_builder import (
    build_root_cause,
    build_l2_analysis,
    build_resolution,   # ✅ ADDED
    merge_with_user_input
)

#============ Date format ====================
def get_formatted_date():
    return datetime.now().strftime("%d-%b-%Y")

#============ Auto Download ====================
def auto_download(file_bytes, filename, mime):
    b64 = base64.b64encode(file_bytes).decode()
    href = f"""
        <a id="download_link" href="data:{mime};base64,{b64}" download="{filename}"></a>
        <script>
            document.getElementById('download_link').click();
        </script>
    """
    return href

#============ CLEAR FUNCTION ====================
def clear_all():
    st.session_state["clear_triggered"] = True
    st.session_state["uploader_reset"] = st.session_state.get("uploader_reset", 0) + 1

    st.session_state["inc_input"] = ""
    st.session_state["bulk_ids"] = ""
    st.session_state["root"] = ""
    st.session_state["l2"] = ""
    st.session_state["res"] = ""

    for key in ["data", "word_file", "pdf_file", "zip_file", "images"]:
        if key in st.session_state:
            del st.session_state[key]

    st.rerun()


def extract_azure_link(text):
    if not text:
        return ""

    text = str(text)

    # ✅ Case 1: Azure URL
    match = re.search(r"/(\d{5,})", text)
    if match:
        return match.group(1)

    # ✅ Case 2: "Azure bug 695698"
    match = re.search(r"azure[^\d]*(\d{5,})", text, re.I)
    if match:
        return match.group(1)

    # ❌ Do NOT fallback to random numbers
    return ""


def get_incident(df, inc):
    df["number"] = df["number"].astype(str).str.upper()
    row = df[df["number"] == inc.upper()]

    if row.empty:
        return None

    r = row.iloc[0]

    # ✅ properly indented
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

        # ✅ FIXED
        "resolution": resolution_text,
        "azure_bug": extract_azure_link(resolution_text),

        "ptc_case": r.get("vendor ticket"),
    }

def render_doc_generator():

    # SAFE INIT
    for key in ["root", "l2", "res", "images"]:
        if key not in st.session_state:
            st.session_state[key] = "" if key != "images" else {"root": [], "l2": [], "res": []}

    st.title("📄 SNOW Incident Report Generator")
    df = load_snow_data()

    # SIDEBAR
    st.sidebar.header("Filters")
    priority_sel = st.sidebar.multiselect("Priority", df["priority"].dropna().unique())
    date_range = st.sidebar.date_input("Created Date Range", [])

    if st.sidebar.button("Apply Filters to Bulk"):
        filtered = df.copy()
        if priority_sel:
            filtered = filtered[filtered["priority"].isin(priority_sel)]
        st.session_state["bulk_ids"] = ", ".join(filtered["number"].astype(str).tolist())

    if st.sidebar.button("Clear All Data"):
        clear_all()

    # INPUTS
    inc = st.text_input("Enter Incident Number", key="inc_input")
    bulk = st.text_area("Bulk Incident Numbers", key="bulk_ids")

    col_fetch, col_word, col_pdf, col_bulk, col_prev = st.columns(5)

    # ================= FETCH =================
    with col_fetch:
        if st.button("Fetch", use_container_width=True):
            data = get_incident(df, inc)

            if data:
                st.session_state["data"] = data

                auto_root = build_root_cause(data["work_notes"])
                auto_l2 = build_l2_analysis(data["comments"])
                auto_res = build_resolution(data["resolution"])   # ✅ FIXED

                st.session_state["root"] = merge_with_user_input(auto_root, st.session_state.get("root"))
                st.session_state["l2"] = merge_with_user_input(auto_l2, st.session_state.get("l2"))
                st.session_state["res"] = merge_with_user_input(auto_res, st.session_state.get("res"))

                st.success("Loaded")
            else:
                st.error("Not found")

    # ================= WORD =================
    with col_word:
        if "data" in st.session_state:
            data = st.session_state["data"]
            incident_no = data.get("number", "incident")

            doc_bytes = generate_word_doc(
                data,
                st.session_state.get("root", ""),
                st.session_state.get("l2", ""),
                st.session_state.get("res", ""),
                st.session_state.get("images")
            )

            st.download_button(
                "Word",
                data=doc_bytes,
                file_name=f"{incident_no}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )

    # ================= PDF =================
    with col_pdf:
        if "data" in st.session_state:
            data = st.session_state["data"]
            incident_no = data.get("number", "incident")

            pdf_bytes = generate_pdf(
                data,
                st.session_state.get("root", ""),
                st.session_state.get("l2", ""),
                st.session_state.get("res", ""),
                st.session_state.get("images")
            )

            st.download_button(
                "PDF",
                data=pdf_bytes,
                file_name=f"{incident_no}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    # ================= BULK =================
    with col_bulk:
        ids = [i.strip() for i in bulk.split(",") if i.strip()]

        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, "w") as z:
            for i in ids:
                d = get_incident(df, i)
                if d:
                    inc_id = d.get("number", "incident")

                    word_bytes = generate_word_doc(d, "", "", "", None)
                    pdf_bytes = generate_pdf(d, "", "", "", None)

                    z.writestr(f"{inc_id}.docx", word_bytes)
                    z.writestr(f"{inc_id}.pdf", pdf_bytes)

        zip_buffer.seek(0)

        st.download_button(
            "Bulk",
            data=zip_buffer,
            file_name=f"Closure-document_{get_formatted_date()}.zip",
            mime="application/zip",
            use_container_width=True
        )

    # ================= EDIT =================
    st.subheader("Edit Report Details")

    reset_id = st.session_state.get("uploader_reset", 0)

    st.text_area("PROBLEM STATEMENT & ROOT CAUSE", key="root")
    root_imgs = st.file_uploader("Root Images", type=["png", "jpg"], accept_multiple_files=True, key=f"root_{reset_id}")

    st.text_area("TECHNICAL ANALYSIS", key="l2")
    l2_imgs = st.file_uploader("L2 Images", type=["png", "jpg"], accept_multiple_files=True, key=f"l2_{reset_id}")

    st.text_area("RESOLUTION & RECOMMENDATION", key="res")
    res_imgs = st.file_uploader("Resolution Images", type=["png", "jpg"], accept_multiple_files=True, key=f"res_{reset_id}")

    st.session_state["images"] = {
        "root": root_imgs or [],
        "l2": l2_imgs or [],
        "res": res_imgs or []
    }
    
    # PREVIEW
    with col_prev:
        show_prev = st.button("Preview", use_container_width=True)

    if show_prev and "data" in st.session_state:
        with st.expander("Report Preview", expanded=True):
            st.write(f"**Short Description:** {st.session_state['data']['short_description']}")
            st.write(f"**Root Cause:** {st.session_state.get('root')}")
