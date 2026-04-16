import streamlit as st
from modules.search_page import render_search_page
from modules.doc_generator_ui import render_doc_generator

st.set_page_config(layout="wide")

menu = st.sidebar.selectbox(
    "📊 Select Module",
    ["Search Dashboard", "Word Report Generator"]
)

# ✅ GLOBAL CSS FIX
st.markdown("""
<style>

/* CENTER ALIGN ALL */
td, th {
    text-align: center !important;
}

/* DESCRIPTION COLUMN */
td:nth-child(3) {
    text-align: left !important;
    max-width: 350px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

th:nth-child(3) {
    text-align: center !important;
}

/* KPI FONT FIX */
[data-testid="stMetricValue"] {
    font-size: 14px !important;
}

/* INPUT HEIGHT */
input, button {
    height: 38px !important;
}

</style>
""", unsafe_allow_html=True)

if menu == "Search Dashboard":
    render_search_page()

elif menu == "Word Report Generator":
    render_doc_generator()
