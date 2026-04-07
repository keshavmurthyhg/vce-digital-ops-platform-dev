import streamlit as st
from modules.data_loader import load_data
from modules.filters import create_filter, apply_filters
from modules.kpi import show_kpi
from modules.search import search_box
from modules.table import show_table

# ---------------- PAGE CONFIG ----------------
st.set_page_config(layout="wide")

# ---------------- TITLE ----------------
# --- TOP BAR ---
col1, col2, col3, col4 = st.columns([1,1,1,6])

with col1:
    if st.button("ALL"):
        st.session_state.source = "ALL"

with col2:
    if st.button("AZURE"):
        st.session_state.source = "AZURE"

with col3:
    if st.button("SNOW"):
        st.session_state.source = "SNOW"

with col4:
    st.markdown("### 📊 Ops Insight Dashboard (DEV)")

# ---------------- LOAD DATA ----------------
df, info = load_data()

if df.empty:
    st.error("❌ Data could not be loaded from sources")
    st.stop()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## ⚙️ Ops Insight Dashboard")
    st.markdown("---")

    # MENU
    st.selectbox("Menu", ["Search Tool"])

    # ---------------- SOURCE ----------------
    st.markdown("### 📂 Source")
    source = st.radio(
        "",
        ["ALL", "AZURE", "SNOW", "PTC"],
        horizontal=True
    )

# ---------------- BASE DATA ----------------
base_df = df if source == "ALL" else df[df["Source"] == source]

# ---------------- FILTERS ----------------
with st.sidebar:
    st.markdown("### 🔧 Filters")

    state = create_filter(base_df, "Status")
    priority = create_filter(base_df, "Priority")

    # Azure-only filter
    if source == "AZURE":
        release = create_filter(base_df, "Release")
    else:
        release = "ALL"

# ---------------- SEARCH ----------------
keyword = search_box()

# ---------------- APPLY FILTERS ----------------
filtered = apply_filters(base_df, state, priority, release, keyword)

# ---------------- RESULTS HEADER ----------------
st.markdown(f"### 📄 Results: {len(filtered)}")

# ---------------- TABLE ----------------
show_table(filtered)

# ---------------- DOWNLOAD ----------------
st.download_button(
    "⬇ Download",
    filtered.to_csv(index=False),
    "filtered_results.csv"
)

# ---------------- KPI (BOTTOM LEFT) ----------------
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📊 KPI")
    show_kpi(base_df)

# ---------------- DATA FRESHNESS ----------------
if info:
    st.caption(f"🕒 Last refreshed: {info.get('last_refresh')}")
