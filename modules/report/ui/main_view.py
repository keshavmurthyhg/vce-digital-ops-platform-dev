import streamlit as st

from modules.common.ui.preview import render_preview
from modules.common.ui.buttons import render_action_buttons
from modules.report.services.rca_service import build_rca
from modules.report.services.data_mapper import map_incident


def render_main(df):

    st.title("Incident Report Generator")

    # ---------------- INCIDENT + FETCH ---------------- #
    col1, col2 = st.columns([5, 1])

    with col1:
        incident = st.selectbox(
            "Select Incident",
            df["number"].dropna().unique(),
            key="incident_select"
        )

    with col2:
        fetch_btn = st.button(
            "Fetch",
            use_container_width=True,
            key="fetch_btn"
        )

    # ---------------- BULK ---------------- #
    st.subheader("Bulk Incident Numbers")

    st.text_area(
        "Enter comma-separated incident numbers",
        key="bulk_incidents",
        height=100
    )

    # ---------------- BUTTONS ---------------- #
    actions = render_action_buttons()

    # ---------------- FETCH ---------------- #
    if fetch_btn:
        try:
            row_raw = df[df["number"] == incident].iloc[0].to_dict()

            # 🔥 Use mapper (single source of truth)
            row = map_incident(row_raw)

            st.session_state["data"] = row

            # RCA
            rca = build_rca(row)
            st.session_state.update(rca)

            st.success("Incident loaded successfully")

        except Exception as e:
            st.error(f"Error loading incident: {e}")

    # ---------------- PREVIEW ---------------- #
    if actions.get("preview"):
        if "data" not in st.session_state:
            st.warning("Please fetch an incident first")
        else:
            render_preview(st.session_state["data"])

    # ---------------- CLEAR ---------------- #
    if actions.get("clear"):
        st.session_state.clear()
        st.rerun()

    # ---------------- RCA SECTION ---------------- #
    if "data" in st.session_state:

        st.subheader("Edit Report Details")

        st.text_area(
            "PROBLEM STATEMENT",
            key="problem",
            height=120
        )

        st.file_uploader(
            "Problem Images",
            accept_multiple_files=True,
            key="problem_images"
        )

        st.text_area(
            "ROOT CAUSE",
            key="root_cause",
            height=150
        )

        st.file_uploader(
            "Root Images",
            accept_multiple_files=True,
            key="root_images"
        )

        st.text_area(
            "RESOLUTION & RECOMMENDATION",
            key="resolution",
            height=150
        )

        st.file_uploader(
            "Resolution Images",
            accept_multiple_files=True,
            key="resolution_images"
        )
