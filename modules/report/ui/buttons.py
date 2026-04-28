import streamlit as st

def render_action_buttons():
    colA, colB, colC, colD, colE = st.columns(5)

    return {
        "pdf": colA.button("Generate PDF", use_container_width=True),
        "word": colB.button("Generate Word", use_container_width=True),
        "bulk": colC.button("Bulk Generate", use_container_width=True),
        "clear": colD.button("Clear", use_container_width=True),
        "preview": colE.button("Preview", use_container_width=True),
    }
