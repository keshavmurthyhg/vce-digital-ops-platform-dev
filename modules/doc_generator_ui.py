import streamlit as st
import pandas as pd
from modules.snow_loader import load_snow_data
from modules.doc_generator import generate_word_doc, generate_pdf
from io import BytesIO
import zipfile
import re


# ✅ CLEAR FUNCTION (SAFE)
def clear_all():
    keys_to_clear = [
        "data",
        "root",
        "l2",
        "res",
        "word_file",
        "pdf_file",
        "zip_file",
        "images",
        "inc_input",
        "bulk_ids",
        "root_img",
        "l2_img",
        "res_img"
    ]

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    st.rerun()


def extract_azure_link(text):
    if not text: return ""
    match = re.search(r"/(\d+)", str(text))
    return match.group(1) if match else ""


def get_incident(df, inc):
    df["number"] = df["number"].astype(str).str.upper()
    row = df[df["number"] == inc.upper()]
    if row.empty: return None
    r = row.iloc[0]
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
        "resolution": r.get("resolution notes", ""),
        "ptc_case": r.get("vendor ticket"),
        "azure_bug": extract_azure_link(r.get("resolution notes"))
    }


def render_doc_generator():
    st.title("📄 SNOW Incident Report Generator")
    df = load_snow_data()

    # SIDEBAR (UNCHANGED)
    st.sidebar.header("Filters")
    priority_sel = st.sidebar.multiselect("Priority", df["priority"].dropna().unique(), key="filter_priority")
    date_range = st.sidebar.date_input("Created Date Range", [], key="filter_date")

    if st.sidebar.button("Apply Filters to Bulk"):
        filtered = df.copy()
        if priority_sel:
            filtered = filtered[filtered["priority"].isin(priority_sel)]
        st.session_state["bulk_ids"] = ", ".join(filtered["number"].astype(str).tolist())

    if st.sidebar.button("Clear All Data"):
        clear_all()

    # INPUTS (UNCHANGED)
    inc = st.text_input("Enter Incident Number", key="inc_input")
    bulk = st.text_area("Bulk Incident Numbers", key="bulk_ids")

    col_fetch, col_word, col_pdf, col_bulk, col_prev = st.columns(5)

    # FETCH (UNCHANGED)
    with col_fetch:
        if st.button("Fetch", use_container_width=True):
            data = get_incident(df, inc)
            if data:
                st.session_state["data"] = data
                st.session_state["root"] = data["work_notes"]
                st.session_state["l2"] = data["comments"]
                st.session_state["res"] = data["resolution"]
                st.success("Loaded")
            else:
                st.error("Not found")

    # WORD (UNCHANGED)
    with col_word:
        if st.button("Word", use_container_width=True):
            if "data" in st.session_state:
                st.session_state["word_file"] = generate_word_doc(
                    st.session_state["data"], st.session_state.get("root", ""),
                    st.session_state.get("l2", ""), st.session_state.get("res", ""),
                    st.session_state.get("images")
                )
        if "word_file" in st.session_state:
            st.download_button("⬇ Word", st.session_state["word_file"], 
                               file_name=f"{st.session_state['data']['number']}.docx", use_container_width=True)

    # PDF (UNCHANGED)
    with col_pdf:
        if st.button("PDF", use_container_width=True):
            if "data" in st.session_state:
                st.session_state["pdf_file"] = generate_pdf(
                    st.session_state["data"], st.session_state.get("root", ""),
                    st.session_state.get("l2", ""), st.session_state.get("res", ""),
                    st.session_state.get("images")
                )
        if "pdf_file" in st.session_state:
            st.download_button("⬇ PDF", st.session_state["pdf_file"], 
                               file_name=f"{st.session_state['data']['number']}.pdf", use_container_width=True)

    # BULK (UNCHANGED)
    with col_bulk:
        if st.button("Bulk", use_container_width=True):
            ids = [i.strip() for i in bulk.split(",") if i.strip()]
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as z:
                for i in ids:
                    d = get_incident(df, i)
                    if d:
                        f = generate_word_doc(d, "", "", "")
                        z.writestr(f"{i}.docx", f.getvalue())
            zip_buffer.seek(0)
            st.session_state["zip_file"] = zip_buffer
        if "zip_file" in st.session_state:
            st.download_button("⬇ ZIP", st.session_state["zip_file"], "reports.zip", use_container_width=True)

    # PREVIEW (UNCHANGED)
    with col_prev:
        show_prev = st.button("Preview", use_container_width=True)

    if show_prev and "data" in st.session_state:
        with st.expander("Report Preview", expanded=True):
            st.write(f"**Short Description:** {st.session_state['data']['short_description']}")
            st.write(f"**Root Cause:** {st.session_state.get('root')}")

    # EDITABLE FIELDS (UNCHANGED)
    st.subheader("Edit Report Details")
    st.text_area("Root Cause", key="root")
    root_img = st.file_uploader("Root Image", type=["png", "jpg"], key="root_img")
    
    st.text_area("L2 Analysis", key="l2")
    l2_img = st.file_uploader("L2 Image", type=["png", "jpg"], key="l2_img")
    
    st.text_area("Resolution", key="res")
    res_img = st.file_uploader("Resolution Image", type=["png", "jpg"], key="res_img")

    st.session_state["images"] = {"root": root_img, "l2": l2_img, "res": res_img}
