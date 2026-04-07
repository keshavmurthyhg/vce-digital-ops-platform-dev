import streamlit as st
from modules.data_loader import load_data
from modules.filters import apply_filters
from modules.table import show_table

st.set_page_config(layout="wide")

# --- COMPACT UI ---
st.markdown("""
<style>
section[data-testid="stSidebar"] {
    font-size: 13px;
}
.stRadio label {
    font-size: 12px !important;
}
.stSelectbox div[data-baseweb="select"] {
    min-height: 30px !important;
}
</style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
df, info = load_data()

if df.empty:
    st.error("❌ Data could not be loaded")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## Ops Insight Dashboard")

    source = st.radio("", ["ALL", "AZURE", "SNOW", "PTC"], horizontal=True)

    st.markdown("### Filters")
    status = st.selectbox("Status", ["ALL"] + sorted(df["Status"].dropna().unique()))
    priority = st.selectbox("Priority", ["ALL"] + sorted(df["Priority"].dropna().unique()))

# --- MAIN ---
st.markdown("<h3>Ops Insight Dashboard</h3>", unsafe_allow_html=True)

keyword = st.text_input("🔎 Search", "")

filtered = apply_filters(df, status=status, priority=priority, keyword=keyword)

# --- SOURCE FILTER ---
if source != "ALL":
    filtered = filtered[filtered["Source"] == source]

st.markdown(f"**Results: {len(filtered)}**")

show_table(filtered)

if info:
    st.caption(f"Last refreshed: {info.get('last_refresh','')}")
