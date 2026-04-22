import streamlit as st
from io import BytesIO
import zipfile
import re

from modules.search.snow_loader import load_snow_data
from modules.report.doc_generator import generate_word, generate_pdf_report


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


def render():

    st.title("📄 SNOW Incident Report Generator")

    df = load_snow_data()

    inc = st.text_input("Enter Incident Number")

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

    if "data" in st.session_state:

        st.subheader("Edit Report")

        st.text_area("Root Cause", key="root")
        st.text_area("L2 Analysis", key="l2")
        st.text_area("Resolution", key="res")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Generate Word"):
                st.session_state["word_file"] = generate_word(
                    st.session_state["data"],
                    st.session_state.get("root", ""),
                    st.session_state.get("l2", ""),
                    st.session_state.get("res", ""),
                    None
                )

            if "word_file" in st.session_state:
                st.download_button(
                    "⬇ Download Word",
                    st.session_state["word_file"],
                    file_name="report.docx"
                )

        with col2:
            if st.button("Generate PDF"):
                st.session_state["pdf_file"] = generate_pdf_report(
                    st.session_state["data"],
                    st.session_state.get("root", ""),
                    st.session_state.get("l2", ""),
                    st.session_state.get("res", ""),
                    None
                )

            if "pdf_file" in st.session_state:
                st.download_button(
                    "⬇ Download PDF",
                    st.session_state["pdf_file"],
                    file_name="report.pdf"
                )
