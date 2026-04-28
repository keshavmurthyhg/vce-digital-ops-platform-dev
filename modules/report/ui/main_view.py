import streamlit as st

from modules.common.ui.components import render_preview_table, render_description_table
from modules.common.ui.buttons import render_buttons
from modules.report.services.rca_service import build_rca


def render_main(df):

    st.title("Incident Report Generator")

    incident = st.selectbox("Select Incident", df["number"].dropna().unique())

    buttons = render_buttons()

    if buttons.get("fetch"):
        row = df[df["number"] == incident].iloc[0].to_dict()
        st.session_state["data"] = row
        st.session_state.update(build_rca(row))
    
    if buttons.get("preview") and "data" in st.session_state:
        render_preview_table(st.session_state["data"])
        render_description_table(st.session_state["data"])
    
    if buttons.get("clear"):
        st.session_state.clear()
        st.rerun()

    if "data" in st.session_state:
    
        st.subheader("Edit Report Details")
    
        # ---------------- PROBLEM ---------------- #
        st.text_area(
            "PROBLEM STATEMENT",
            key="problem",
            height=120
        )

        # Upload Root Images
        st.file_uploader(
            "Problem Images",
            accept_multiple_files=True,
            key="problem_images"
    
        # ---------------- ROOT CAUSE ---------------- #
        st.text_area(
            "ROOT CAUSE",
            key="root_cause",
            height=150
        )
    
        # Upload Root Images
        st.file_uploader(
            "Root Images",
            accept_multiple_files=True,
            key="root_images"
        )
    
        # ---------------- RESOLUTION ---------------- #
        st.text_area(
            "RESOLUTION & RECOMMENDATION",
            key="resolution",
            height=150
        )
    
        # Upload Resolution Images
        st.file_uploader(
            "Resolution Images",
            accept_multiple_files=True,
            key="resolution_images"
        )
