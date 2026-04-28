import streamlit as st

from modules.common.ui.components import render_preview_table, render_description_table
from modules.common.ui.buttons import render_buttons
from modules.report.services.rca_service import build_rca


def render_main(df):

    st.title("Incident Report Generator")

    # ---------------- INCIDENT ---------------- #
    #incident = st.selectbox("Select Incident", df["number"].dropna().unique())
    col1, col2 = st.columns([5,1])
    
    with col1:
        incident = st.selectbox(
            "Select Incident",
            df["number"].dropna().unique(),
            key="incident_select"
        )
    
    with col2:
        fetch_btn = st.button("Fetch", use_container_width=True)
    

    # ---------------- BULK ---------------- #
    st.subheader("Bulk Incident Numbers")

    bulk_input = st.text_area(
        "Enter comma-separated incident numbers",
        key="bulk_incidents",
        height=100
    )

    # ---------------- BUTTONS ---------------- #
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        fetch_btn = st.button("Fetch")
    with col2:
        pdf_btn = st.button("Generate PDF")
    with col3:
        word_btn = st.button("Generate Word")
    with col4:
        bulk_btn = st.button("Bulk Generate")
    with col5:
        preview_btn = st.button("Preview")

    clear_btn = st.button("Clear")

    # ---------------- APPLY TO BULK ---------------- #
    if st.sidebar.button("Apply to Bulk"):

        if "data" in st.session_state:
            inc = st.session_state["data"].get("number")

            existing = st.session_state.get("bulk_incidents", "")

            if inc and inc not in existing:
                if existing:
                    st.session_state["bulk_incidents"] = existing + "," + inc
                else:
                    st.session_state["bulk_incidents"] = inc

    # ---------------- FETCH ---------------- #
    if fetch_btn:
        row = df[df["number"] == incident].iloc[0].to_dict()

        # 🔴 FIX KEY MAPPING
        row["short_description"] = row.get("short_description") or row.get("short description")

        st.session_state["data"] = row
        st.session_state.update(build_rca(row))

    # ---------------- PREVIEW ---------------- #
    if preview_btn and "data" in st.session_state:

        from modules.common.ui.preview import render_preview
        render_preview(st.session_state["data"])

    # ---------------- CLEAR ---------------- #
    if clear_btn:
        st.session_state.clear()
        st.rerun()

    # ---------------- RCA SECTION ---------------- #
    if "data" in st.session_state:

        st.subheader("Edit Report Details")

        st.text_area("PROBLEM STATEMENT", key="problem", height=120)

        st.file_uploader(
            "Problem Images",
            accept_multiple_files=True,
            key="problem_images"
        )

        st.text_area("ROOT CAUSE", key="root_cause", height=150)

        st.file_uploader(
            "Root Images",
            accept_multiple_files=True,
            key="root_images"
        )

        st.text_area("RESOLUTION & RECOMMENDATION", key="resolution", height=150)

        st.file_uploader(
            "Resolution Images",
            accept_multiple_files=True,
            key="resolution_images"
        )
