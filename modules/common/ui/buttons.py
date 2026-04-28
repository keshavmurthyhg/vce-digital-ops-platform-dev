import streamlit as st

def render_buttons():
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    fetch   = col1.button("Fetch")
    preview = col2.button("Preview")
    clear   = col3.button("Clear")
    word    = col4.button("Generate Word")
    pdf     = col5.button("Generate PDF")
    bulk    = col6.button("Bulk Generate")
    
