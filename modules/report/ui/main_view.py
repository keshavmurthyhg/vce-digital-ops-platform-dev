import streamlit as st

from modules.common.ui.preview import render_preview
from modules.common.ui.buttons import render_action_buttons
from modules.report.services.rca_service import build_rca


def render_main(df):

    st.title("Incident Report Generator")

    # ---------------- INCIDENT + FETCH ---------------- #
    col1, col2 = st.columns([5,1])

    with col1:
        incident = st.selectbox(
            "Select Incident",
            df["number"].dropna().unique(),
            key="incident_select"
        )

    with col2:
        fetch_btn = st.button("Fetch", use_container_width=True, key="fetch_btn")

    # ---------------- BULK ---------------- #
    st.subheader("Bulk Incident Numbers")

    st.text_area(
        "Enter comma-separated incident numbers",
        key="bulk_incidents",
        height=100
    )

    # ---------------- BUTTONS (CLEAN) ---------------- #
    actions = render_action_buttons()

    # ---------------- FETCH ---------------- #
    if fetch_btn:
        row_raw = df[df["number"] == incident].iloc[0].to_dict()
    
        # 🔥 STANDARDIZE KEYS
        def get_display(val):
            if isinstance(val, dict):
                return val.get("display_value") or val.get("value")
            return val
        
        
        row = {
            "number": row_raw.get("number"),
        
            "short_description": (
                row_raw.get("short_description")
                or row_raw.get("short description")
                or "-"
            ),
        
            "description": row_raw.get("description") or "-",
        
            "priority": get_display(row_raw.get("priority")) or "-",
        
            "opened_by": get_display(
                row_raw.get("opened_by") or row_raw.get("sys_created_by")
            ) or "-",
        
            "assigned_to": get_display(row_raw.get("assigned_to")) or "-",
        
            "created": (
                row_raw.get("sys_created_on")
                or row_raw.get("opened_at")
                or row_raw.get("created")
            ),
        
            "resolved": (
                row_raw.get("closed_at")
                or row_raw.get("resolved_at")
            ),
        
            # 🔥 CRITICAL (your missing fields)
            "azure_bug": (
                row_raw.get("azure_bug")
                or row_raw.get("u_azure_bug")
                or "-"
            ),
        
            "ptc_case": (
                row_raw.get("ptc_case")
                or row_raw.get("u_ptc_case")
                or "-"
            ),
        }
    
        st.session_state["data"] = row
        st.session_state.update(build_rca(row))

    # ---------------- PREVIEW ---------------- #
    if actions["preview"] and "data" in st.session_state:
        render_preview(st.session_state["data"])

    # ---------------- CLEAR ---------------- #
    if actions["clear"]:
        st.session_state.clear()
        st.rerun()

    # ---------------- RCA ---------------- #
    if "data" in st.session_state:

        st.subheader("Edit Report Details")

        st.text_area("PROBLEM STATEMENT", key="problem", height=120)

        st.file_uploader("Problem Images", accept_multiple_files=True, key="problem_images")

        st.text_area("ROOT CAUSE", key="root_cause", height=150)

        st.file_uploader("Root Images", accept_multiple_files=True, key="root_images")

        st.text_area("RESOLUTION & RECOMMENDATION", key="resolution", height=150)

        st.file_uploader("Resolution Images", accept_multiple_files=True, key="resolution_images")
