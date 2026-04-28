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
