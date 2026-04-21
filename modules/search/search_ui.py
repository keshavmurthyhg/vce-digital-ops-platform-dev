import streamlit as st
from .logic import load_data, process_data

def render():
    st.title("🔍 Search Dashboard")

    uploaded_file = st.file_uploader("Upload File")

    if uploaded_file:
        data = load_data(uploaded_file)
        result = process_data(data)

        st.write(result)

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
