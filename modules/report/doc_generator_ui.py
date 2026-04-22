import streamlit as st
import pandas as pd
from modules.report.snow_loader import load_snow_data
from modules.report.doc_generator import generate_word_doc, generate_pdf
from io import BytesIO
import zipfile
import re


def clear_all():
    st.session_state.clear()
    st.rerun()


def extract_azure_link(text):
    if not text:
        return ""
    match = re.search(r"/(\d+)", str(text))
    return match.group(1) if match else ""


def get_incident(df, inc):
    df["number"] = df["number"].astype(str).str.upper()
    row = df[df["number"] == inc.upper()]
    if row.empty:
        return None
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

    inc = st.text_input("Enter Incident Number")
    col1, col2, col3 = st.columns(3)

    # FETCH
    with col1:
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

    # WORD
    with col2:
        if st.button("Generate Word"):
            if "data" in st.session_state:
                st.session_state["word"] = generate_word_doc(
                    st.session_state["data"],
                    st.session_state.get("root"),
                    st.session_state.get("l2"),
                    st.session_state.get("res")
                )

    # PDF
    with col3:
        if st.button("Generate PDF"):
            if "data" in st.session_state:
                st.session_state["pdf"] = generate_pdf(
                    st.session_state["data"],
                    st.session_state.get("root"),
                    st.session_state.get("l2"),
                    st.session_state.get("res")
                )

    # DOWNLOADS
    if "word" in st.session_state:
        st.download_button("⬇ Download Word",
            st.session_state["word"],
            file_name=f"{st.session_state['data']['number']}.docx")

    if "pdf" in st.session_state:
        st.download_button("⬇ Download PDF",
            st.session_state["pdf"],
            file_name=f"{st.session_state['data']['number']}.pdf")

    # EDIT FIELDS
    st.subheader("Edit Content")
    st.text_area("Root Cause", key="root")
    st.text_area("L2 Analysis", key="l2")
    st.text_area("Resolution", key="res")

    if st.button("Clear"):
        clear_all()
