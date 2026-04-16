import streamlit as st
from modules.search_page import render_search_page
from modules.doc_generator_ui import render_doc_generator

st.set_page_config(layout="wide")

# ================= MENU =================
menu = st.sidebar.selectbox(
    "📊 Select Module",
    ["Search Dashboard", "Word Report Generator"]
)

# ================= CSS =================
st.markdown("""
<style>

/* CENTER ALIGN ALL */
td, th {
    text-align: center !important;
}

/* EXCEPT DESCRIPTION VALUES */
td:nth-child(3) {
    text-align: left !important;
}

/* HEADER CENTER INCLUDING DESCRIPTION */
th:nth-child(3) {
    text-align: center !important;
}

</style>
""", unsafe_allow_html=True)

# ================= ROUTING =================
if menu == "Search Dashboard":
    render_search_page()

elif menu == "Word Report Generator":
    render_doc_generator()
