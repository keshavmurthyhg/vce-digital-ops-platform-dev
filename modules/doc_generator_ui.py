import streamlit as st
import pandas as pd
from modules.snow_loader import load_snow_data
from modules.doc_generator import generate_word_doc, generate_pdf
from io import BytesIO
import zipfile
import re


# ✅ SAFE CLEAR (FIXED)
def clear_all():
    keys_to_keep = ["active_page"]  # adjust if your nav key is different
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
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

    # SIDEBAR
    st.sidebar.header("Filters")
    priority_sel = st.sidebar.multiselect("Priority", df["priority"].dropna().unique())
    
    if st.sidebar.button("Apply Filters to Bulk"):
        filtered = df.copy()
        if priority_sel:
            filtered = filtered[filtered["priority"].isin(priority_sel)]
        st.session_state["bulk_ids"] = ", ".join(filtered["number"].astype(str))

    if st.sidebar.button("Clear All Data"):
        clear_all()

    inc = st.text_input("Enter Incident Number")
    bulk = st.text_area("Bulk Incident Numbers", key="bulk_ids")

    col_fetch, col_word, col_pdf, col_bulk, col_prev = st.columns(5)

    with col_fetch:
        if st.button("Fetch"):
            data = get_incident(df, inc)
            if data:
                st.session_state["data"] = data
                st.session_state["root"] = data["work_notes"]
                st.session_state["l2"] = data["comments"]
                st.session_state["res"] = data["resolution"]
                st.success("Loaded")
            else:
                st.error("Not found")

    with col_word:
        if st.button("Word"):
            if "data" in st.session_state:
                st.session_state["word_file"] = generate_word_doc(
                    st.session_state["data"],
                    st.session_state.get("root",""),
                    st.session_state.get("l2",""),
                    st.session_state.get("res","")
                )
        if "word_file" in st.session_state:
            st.download_button("⬇ Word", st.session_state["word_file"],
                               file_name=f"{st.session_state['data']['number']}.docx")

    with col_pdf:
        if st.button("PDF"):
            if "data" in st.session_state:
                st.session_state["pdf_file"] = generate_pdf(
                    st.session_state["data"],
                    st.session_state.get("root",""),
                    st.session_state.get("l2",""),
                    st.session_state.get("res","")
                )
        if "pdf_file" in st.session_state:
            st.download_button("⬇ PDF", st.session_state["pdf_file"],
                               file_name=f"{st.session_state['data']['number']}.pdf")

    with col_bulk:
        if st.button("Bulk"):
            ids = [i.strip() for i in bulk.split(",") if i.strip()]
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as z:
                for i in ids:
                    d = get_incident(df, i)
                    if d:
                        f = generate_word_doc(d, "", "", "")
                        z.writestr(f"{i}.docx", f.getvalue())
            zip_buffer.seek(0)
            st.download_button("⬇ ZIP", zip_buffer, "reports.zip")

    with col_prev:
        if st.button("Preview") and "data" in st.session_state:
            st.write(st.session_state["data"])
