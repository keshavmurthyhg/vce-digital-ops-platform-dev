import streamlit as st

from modules.search_page import render_search_page
from modules.doc_generator_ui import render_doc_generator
from modules.charts_page import render_charts_page

st.set_page_config(layout="wide")

# ---------- SIDEBAR ----------
st.sidebar.markdown("## 📊 Module")

if "page" not in st.session_state:
    st.session_state.page = "Search Dashboard"

page = st.sidebar.selectbox(
    "Module",
    [
        "Search Dashboard",
        "Insights Dashboard",
        "Word Report Generator"
    ],
    index=[
        "Search Dashboard",
        "Insights Dashboard",
        "Word Report Generator"
    ].index(st.session_state.page),
    key="page_selector"
)

# ✅ Persist selection
st.session_state.page = page

# ---------- ROUTING ----------
if page == "Search Dashboard":
    render_search_page()

elif page == "Insights Dashboard":
    render_charts_page()

elif page == "Word Report Generator":
    render_doc_generator()

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
