import streamlit as st

from modules.common.ui.components import (
    render_preview_table,
    render_description_table
)


def render_preview(data):
    st.subheader("Preview")

    render_preview_table(data)
    render_description_table(data)
