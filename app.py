import streamlit as st
from modules.data_loader import load_data
from modules.filters import apply_filters
from modules.kpi import show_kpi
from modules.table import show_table

# --- PAGE CONFIG ---
st.set_page_config(layout="wide")

# --- LOAD DATA ---
df, info = load_data()

if df.empty:
    st.error("❌ Data could not be loaded from sources")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## Ops Insight Dashboard")

    st.markdown("### Source")
    source = st.radio("", ["ALL", "AZURE", "SNOW", "PTC"], horizontal=True)

    st.markdown("### Filters")

    status = st.selectbox("Status", ["ALL"] + sorted(df["Status"].dropna().unique().tolist()))
    priority = st.selectbox("Priority", ["ALL"] + sorted(df["Priority"].dropna().unique().tolist()))

# --- MAIN AREA ---

# Title
st.markdown(
    "<h3 style='margin-bottom:10px;'>Ops Insight Dashboard</h3>",
    unsafe_allow_html=True
)

# Search
keyword = st.text_input("🔎 Search", "")

# --- APPLY FILTERS ---
filtered = apply_filters(
    df,
    status=status,
    priority=priority,
    keyword=keyword
)

# --- RESULTS ---
st.markdown(
    f"<div style='font-size:16px; font-weight:600;'>Results: {len(filtered)}</div>",
    unsafe_allow_html=True
)

# --- KPI ---
show_kpi(filtered)

# --- TABLE ---
show_table(filtered)

# --- FOOTER ---
if info:
    st.caption(f"Last refreshed: {info.get('last_refresh', '')}")
