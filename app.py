import streamlit as st
from modules.data_loader import load_data
from modules.filters import create_filter, apply_filters
from modules.kpi import show_kpi
from modules.search import search_box
from modules.table import show_table

st.set_page_config(layout="wide")

# ---------------- PAGE TITLE ----------------
st.sidebar.markdown("## ⚙️ Ops Insight Dashboard")
st.sidebar.markdown("---")

st.sidebar.selectbox("Menu", ["Search Tool"])

# ---------------- LOAD DATA ----------------
df, data_info = load_data()

# ---------------- ERROR HANDLING ----------------
if df.empty:
    st.error("⚠️ Data could not be loaded from sources")
    st.stop()

# ---------------- SOURCE ----------------
st.sidebar.markdown("### Source")

source = st.sidebar.radio(
    "",
    ["ALL", "AZURE", "SNOW", "PTC"],
    horizontal=True
)

# Base dataset
base_df = df if source == "ALL" else df[df["Source"] == source]

# ---------------- FILTERS ----------------
st.sidebar.markdown("### 🔧 Filters")

state = create_filter(base_df, "Status")
priority = create_filter(base_df, "Priority")

release = "ALL"
if source == "AZURE":
    release = create_filter(base_df, "Release")

# ---------------- SEARCH ----------------
keyword = search_box()

# ---------------- APPLY FILTER ----------------
filtered = apply_filters(base_df, state, priority, release, keyword)

# ---------------- DATA STATUS ----------------
st.markdown("### 📊 Data Status")

col1, col2, col3 = st.columns(3)

col1.metric("SNOW", data_info.get("SNOW", "NA"))
col2.metric("PTC", data_info.get("PTC", "NA"))
col3.metric("AZURE", data_info.get("AZURE", "NA"))

# ---------------- REFRESH BUTTON ----------------
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# ---------------- TABLE ----------------
show_table(filtered)

# ---------------- KPI ----------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 KPI")
show_kpi(base_df)
