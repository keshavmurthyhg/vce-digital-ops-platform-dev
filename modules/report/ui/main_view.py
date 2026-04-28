import streamlit as st

from modules.common.ui.components import render_preview_table, render_description_table
from modules.report.utils.rca_generator import generate_rca


def render_main(df):

    st.title("Incident Report Generator")

    col1, col2 = st.columns([4, 1])

    with col1:
        incident = st.selectbox("Select Incident", df["number"].dropna().unique())

    with col2:
        st.write("")
        st.write("")
        fetch = st.button("Fetch", use_container_width=True)

    if fetch:
        data = df[df["number"] == incident].iloc[0].to_dict()
        st.session_state["data"] = data

        rca = generate_rca(data)
        st.session_state.update(rca)

    if "data" in st.session_state:

        st.markdown("### Preview")
        render_preview_table(st.session_state["data"])
        render_description_table(st.session_state["data"])
