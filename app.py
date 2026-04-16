import streamlit as st
from modules.search_page import render_search_page
from modules.doc_generator_ui import render_doc_generator

st.set_page_config(layout="wide")


menu = st.sidebar.selectbox("st.sidebar.markdown("## 📊 Module")",
        ["Search Dashboard", "Word Report Generator"]
)

# ✅ GLOBAL CSS FIX
st.markdown("""
<style>

section[data-testid="stSidebar"] label {
    font-size: 14px !important;
    font-weight: 600 !important;
}

table {
    width: 100%;
    border-collapse: collapse;
}

/* FORCE NO WRAP FOR ALL CELLS */
td, th {
    white-space: nowrap !important;
    text-align: center !important;
}

/* DESCRIPTION COLUMN */
td:nth-child(3) {
    text-align: left !important;
    max-width: 350px;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* HEADER CENTER */
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
