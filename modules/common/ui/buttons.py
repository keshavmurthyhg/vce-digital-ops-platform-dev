import streamlit as st

def render_buttons():
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        fetch = st.button("Fetch")

    with col2:
        preview = st.button("Preview")

    with col3:
        clear = st.button("Clear")
        
    with col4:
        word = st.button("Generate Word")

    with col5:
        pdf = st.button("Generate PDF")

    with col6:
        bulk = st.button("Bulk Generate")

    return {
        "fetch": fetch,
        "pdf": pdf,
        "word": word,
        "bulk": bulk,
        "preview": preview,
        "clear": clear
    }
