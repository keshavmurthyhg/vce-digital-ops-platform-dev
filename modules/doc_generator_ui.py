import streamlit as st
import pandas as pd
from modules.snow_loader import load_snow_data
from modules.doc_generator import generate_word_doc, generate_pdf
from io import BytesIO
import zipfile
import re


# ================= CLEAN SESSION =================
def clear_all():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()


# ================= AZURE =================
def extract_azure_link(text):
    if not text:
        return ""
    match = re.search(r"/(\d+)", str(text))
    return match.group(1) if match else ""


# ================= FETCH =================
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
        "created_date": r.get("created"),
        "assigned_to": r.get("assigned to"),
        "resolved_date": r.get("resolved"),
        "work_notes": r.get("work notes"),
        "comments": r.get("additional comments"),
        "resolution": r.get("resolution notes"),
        "ptc_case": r.get("vendor ticket"),
        "azure_bug": extract_azure_link(r.get("resolution notes"))
    }


# ================= UI =================
def render_doc_generator():

    st.title("📄 SNOW Incident Report Generator")

    df = load_snow_data()

    # ================= SIDEBAR =================
    st.sidebar.header("Filters")

    priority = st.sidebar.multiselect("Priority", df["priority"].dropna().unique())

    state = []
    if "state" in df.columns:
        df["state"] = df["state"].fillna("Unknown")
        state = st.sidebar.multiselect("State", df["state"].unique())

    date = st.sidebar.date_input("Created Date Range", [])

    if st.sidebar.button("Apply Filters to Bulk"):
        st.session_state["bulk_ids"] = ", ".join(df["number"].astype(str).unique())

    if st.sidebar.button("Clear"):
        clear_all()

    # ================= INPUT =================
    inc = st.text_input("Enter Incident Number")

    bulk = st.text_area("Bulk Incident Numbers", key="bulk_ids")

    # ================= STATUS =================
    status = st.empty()

    # ================= BUTTON ROW =================
    col1, col2, col3, col4, col5 = st.columns(5)

    # FETCH
    if col1.button("Fetch"):
        data = get_incident(df, inc)
        if data:
            st.session_state["data"] = data
            st.session_state["root"] = data["work_notes"]
            st.session_state["l2"] = data["comments"]
            st.session_state["res"] = data["resolution"]
            status.success("Incident loaded")
        else:
            status.error("Incident not found")

    # WORD
    if col2.button("Word"):
        if "data" in st.session_state:
            st.session_state["word"] = generate_word_doc(
                st.session_state["data"],
                st.session_state["root"],
                st.session_state["l2"],
                st.session_state["res"]
            )
            status.success("Word generated")

    if "word" in st.session_state:
        col2.download_button("⬇", st.session_state["word"], "report.docx")

    # PDF
    if col3.button("PDF"):
        if "data" in st.session_state:
            st.session_state["pdf"] = generate_pdf(
                st.session_state["data"],
                st.session_state["root"],
                st.session_state["l2"],
                st.session_state["res"]
            )
            status.success("PDF generated")

    if "pdf" in st.session_state:
        col3.download_button("⬇", st.session_state["pdf"], "report.pdf")

    # BULK
    if col4.button("Bulk"):
        ids = [i.strip() for i in bulk.split(",") if i.strip()]
        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, "w") as z:
            for i in ids:
                d = get_incident(df, i)
                if d:
                    f = generate_word_doc(d, "", "", "")
                    z.writestr(f"{i}.docx", f.getvalue())

        zip_buffer.seek(0)
        st.session_state["zip"] = zip_buffer
        status.success("Bulk ready")

    if "zip" in st.session_state:
        col4.download_button("⬇ ZIP", st.session_state["zip"], "reports.zip")

    # PREVIEW
    if col5.button("Preview"):
        if "data" in st.session_state:
            st.json(st.session_state["data"])

    # ================= TEXT + IMAGE =================
    st.text_area("Root Cause", key="root")
    st.file_uploader("Root Image", type=["png","jpg"])

    st.text_area("L2 Analysis", key="l2")
    st.file_uploader("L2 Image", type=["png","jpg"])

    st.text_area("Resolution", key="res")
    st.file_uploader("Resolution Image", type=["png","jpg"])
