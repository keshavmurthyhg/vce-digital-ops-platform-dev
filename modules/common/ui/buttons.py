import streamlit as st

def render_buttons():
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        fetch = st.button("Fetch")

    with col2:
        pdf = st.button("Generate PDF")

    with col3:
        word = st.button("Generate Word")

    with col4:
        bulk = st.button("Bulk Generate")

    with col5:
        preview = st.button("Preview")

    clear = st.button("Clear")

    return {
        "fetch": fetch,
        "pdf": pdf,
        "word": word,
        "bulk": bulk,
        "preview": preview,
        "clear": clear
    }
