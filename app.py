import streamlit as st
from modules.data_loader import load_data
from modules.filters import apply_filters
from modules.kpi import show_kpi
from modules.table import show_table

# --- PAGE CONFIG ---
st.set_page_config(layout="wide")

# --- GLOBAL UI CLEANUP ---
st.markdown("""
<style>

/* Reduce overall padding */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
}

/* Sidebar spacing */
section[data-testid="stSidebar"] > div {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

/* Reduce gaps */
.stSelectbox, .stRadio, .stMarkdown {
    margin-bottom: 0.3rem !important;
}

/* Smaller headings */
h1, h2, h3 {
    margin-bottom: 0.3rem !important;
}

</style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
df, info = load_data()

if df.empty:
    st.error("❌ Data could not be loaded from sources")
    st.stop()

# --- TITLE ---
st.markdown(
    "<div style='font-size:20px; font-weight:600;'>Ops Insight Dashboard</div>",
    unsafe_allow_html=True
)

# --- SEARCH ---
keyword = st.text_input("🔎 Search")

# --- FILTERS ---
status = st.selectbox("Status", ["ALL"] + sorted(df["Status"].dropna().unique().tolist()))
priority = st.selectbox("Priority", ["ALL"] + sorted(df["Priority"].dropna().unique().tolist()))

# --- APPLY FILTERS ---
filtered = apply_filters(df, status=status, priority=priority, keyword=keyword)

# --- RESULTS HEADER ---
st.markdown(
    f"<div style='font-size:16px; font-weight:600;'>Results: {len(filtered)}</div>",
    unsafe_allow_html=True
)

# --- KPI ---
show_kpi(filtered)

# --- TABLE ---
show_table(filtered)

# --- DATA FRESHNESS ---
if info:
    st.caption(f"Last refreshed: {info.get('last_refresh', '')}")
