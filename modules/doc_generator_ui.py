import streamlit as st
import pandas as pd
from modules.snow_loader import load_snow_data
from modules.doc_generator import generate_word_doc, generate_pdf
import re
from io import BytesIO
import zipfile


# ================= AZURE ID =================
def extract_azure_link(text):
    if not text:
        return ""
    match = re.search(r"/(\d+)", str(text))
    return match.group(1) if match else ""


# ================= DATE FORMAT =================
def format_date(date_val):
    if not date_val:
        return ""
    try:
        return pd.to_datetime(date_val).strftime("%d-%b-%Y")
    except:
        return str(date_val)


# ================= FETCH =================
def get_incident_from_df(df, incident_number):

    df_copy = df.copy()
    df_copy["number"] = df_copy["number"].astype(str).str.strip().str.upper()
    incident_number = incident_number.strip().upper()

    row = df_copy[df_copy["number"] == incident_number]

    if not row.empty:
        row = row.iloc[0]

        return {
            "number": row.get("number", ""),
            "short_description": row.get("short description", ""),
            "description": row.get("description", ""),

            "priority": row.get("priority", ""),
            "created_by": row.get("caller", ""),
            "created_date": format_date(row.get("created", "")),
            "assigned_to": row.get("assigned to", ""),
            "resolved_date": format_date(row.get("resolved", "")),

            "work_notes": row.get("work notes", ""),
            "comments": row.get("additional comments", ""),
            "resolution": row.get("resolution notes", ""),

            "ptc_case": row.get("vendor ticket", ""),
            "azure_bug": extract_azure_link(row.get("resolution notes", ""))
        }

    return None


# ================= UI =================
def render_doc_generator():

    st.title("📄 SNOW Incident Report Generator")

    df = load_snow_data()

    # SIDEBAR
    st.sidebar.header("Filters")

    priority_filter = st.sidebar.multiselect(
        "Priority",
        options=df["priority"].dropna().unique()
    )

    state_filter = st.sidebar.multiselect(
        "State",
        options=df["state"].dropna().unique() if "state" in df.columns else []
    )

    date_filter = st.sidebar.date_input("Created Date Range", [])

    # APPLY FILTER
    filtered_df = df.copy()

    if priority_filter:
        filtered_df = filtered_df[filtered_df["priority"].isin(priority_filter)]

    if state_filter and "state" in df.columns:
        filtered_df = filtered_df[filtered_df["state"].isin(state_filter)]

    if len(date_filter) == 2:
        filtered_df["created"] = pd.to_datetime(filtered_df["created"], errors="coerce")
        filtered_df = filtered_df[
            (filtered_df["created"] >= pd.to_datetime(date_filter[0])) &
            (filtered_df["created"] <= pd.to_datetime(date_filter[1]))
        ]

    df = filtered_df

    incident_number = st.text_input("Enter Incident Number")
    bulk_ids = st.text_area("Bulk Incident Numbers (comma separated)")

    # ================= BUTTON ROW =================
    col1, col2, col3, col4, col5 = st.columns(5)

    # FETCH
    if col1.button("Fetch"):
        data = get_incident_from_df(df, incident_number)
        if data:
            st.session_state["doc_data"] = data
            st.session_state["root"] = data.get("work_notes", "")
            st.session_state["l2"] = data.get("comments", "")
            st.session_state["res"] = data.get("resolution", "")
            st.success("✅ Loaded")

    # GENERATE WORD
    if col2.button("Word"):
        if "doc_data" in st.session_state:
            st.session_state["word"] = generate_word_doc(
                st.session_state["doc_data"],
                st.session_state["root"],
                st.session_state["l2"],
                st.session_state["res"]
            )

    # GENERATE PDF
    if col3.button("PDF"):
        if "doc_data" in st.session_state:
            st.session_state["pdf"] = generate_pdf(
                st.session_state["doc_data"],
                st.session_state["root"],
                st.session_state["l2"],
                st.session_state["res"]
            )

    # BULK
    if col4.button("Bulk"):
        ids = [i.strip().upper() for i in bulk_ids.split(",") if i.strip()]
        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for inc in ids:
                data = get_incident_from_df(df, inc)
                if data:
                    file = generate_word_doc(data, "", "", "")
                    zf.writestr(f"{inc}.docx", file.getvalue())

        zip_buffer.seek(0)
        st.download_button("Download ZIP", zip_buffer, "reports.zip")

    # DOWNLOAD
    if "word" in st.session_state:
        col5.download_button("Download", st.session_state["word"], "report.docx")

    if "pdf" in st.session_state:
        col5.download_button("Download PDF", st.session_state["pdf"], "report.pdf")

    # TEXT AREAS
    st.text_area("Root Cause", key="root")
    st.text_area("L2 Analysis", key="l2")
    st.text_area("Resolution", key="res")
