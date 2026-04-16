import streamlit as st
from modules.data_loader import load_data
from modules.doc_generator import generate_word_doc


def get_incident_from_df(df, incident_number):

    df_copy = df.copy()
    df_copy.columns = df_copy.columns.str.strip().str.lower()

    row = df_copy[df_copy["number"].astype(str) == str(incident_number)]

    if not row.empty:
        row = row.iloc[0]

        return {
            "number": str(row.get("number", "")),
            "short_description": str(row.get("short description", "")),
            "description": str(row.get("description", "")),
            "priority": str(row.get("priority", "")),
            "state": str(row.get("status", "")),
            "work_notes": str(row.get("work notes", "")),
            "comments": str(row.get("additional comments", "")),
            "resolution": str(row.get("resolution notes", ""))
        }

    return None


def render_doc_generator():

    st.title("📄 SNOW Incident Report Generator")

    df, _ = load_data()

    incident_number = st.text_input("Enter Incident Number", key="snow_input")

    col1, col2 = st.columns(2)

    if col1.button("Fetch Incident"):
        data = get_incident_from_df(df, incident_number)

        if data:
            st.session_state.snow_data = data
            st.session_state.root = data.get("work_notes", "")
            st.session_state.l2 = data.get("comments", "")
            st.session_state.res = data.get("resolution", "")
            st.session_state.closure = data.get("resolution", "")

    if "snow_data" in st.session_state:

        data = st.session_state.snow_data

        root_cause = st.text_area("Root Cause", key="root")
        l2_analysis = st.text_area("L2 Analysis", key="l2")
        resolution = st.text_area("Resolution", key="res")
        closure = st.text_area("Closure Notes", key="closure")

        if col2.button("Generate Document"):

            file = generate_word_doc(
                data,
                root_cause,
                l2_analysis,
                resolution,
                closure
            )

            st.download_button(
                label="📥 Download Report",
                data=file,
                file_name=f"{data.get('number')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
