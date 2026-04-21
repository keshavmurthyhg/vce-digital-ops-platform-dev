import streamlit as st

from modules.search.search_page import render_search_page
from modules.report.doc_generator_ui import render_doc_generator
from modules.analytic.charts_page import render_charts_page
from modules.excel_compare.ui import show_excel_compare

st.set_page_config(layout="wide")

# ---------- SIDEBAR ----------
st.sidebar.markdown("## 📊 Module")

options = [
    "Search Dashboard",
    "Insights Dashboard",
    "Word Report Generator",
    "Excel Compare"
]

# ✅ ALWAYS RESET INVALID VALUES
current_page = st.session_state.get("page", "Search Dashboard")

if current_page not in options:
    current_page = "Search Dashboard"

# ✅ Safe selectbox (NO .index crash)
page = st.sidebar.selectbox(
    "Module",
    options,
    index=options.index(current_page)
)

# ✅ Store safely
st.session_state.page = page

# ---------- ROUTING ----------
if page == "Search Dashboard":
    render_search_page()

elif page == "Insights Dashboard":
    render_charts_page()

elif page == "Word Report Generator":
    render_doc_generator()
elif page == "Excel Compare":
        show_excel_compare()

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
