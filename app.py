import streamlit as st
import pandas as pd
from modules.data_loader import load_data

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(layout="wide")
st.title("📊 Ops Insight Dashboard (DEV)")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
df, info = load_data()

# Safety check
if df.empty:
    st.error("⚠️ Data could not be loaded from sources")
    st.stop()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.header("Menu")

# Source selection (horizontal radio)
source = st.sidebar.radio(
    "Source",
    ["ALL", "AZURE", "SNOW", "PTC"],
    horizontal=True
)

# --------------------------------------------------
# FILTER DATA BASED ON SOURCE
# --------------------------------------------------
filtered_df = df.copy()

if source != "ALL":
    filtered_df = filtered_df[filtered_df["Source"] == source]

# --------------------------------------------------
# KPI (Dynamic)
# --------------------------------------------------
total = len(filtered_df)

open_count = filtered_df["Status"].astype(str).str.contains(
    "Open|New|Active", case=False, na=False
).sum()

closed = filtered_df["Status"].astype(str).str.contains(
    "Closed", case=False, na=False
).sum()

cancelled = filtered_df["Status"].astype(str).str.contains(
    "Cancel", case=False, na=False
).sum()

# KPI layout (compact)
st.sidebar.markdown("### 📊 KPI")

k1, k2 = st.sidebar.columns(2)
k1.metric("Total", total)
k2.metric("Open", open_count)

k3, k4 = st.sidebar.columns(2)
k3.metric("Closed", closed)
k4.metric("Cancelled", cancelled)

# --------------------------------------------------
# SEARCH BAR
# --------------------------------------------------
st.subheader("🔍 Search")

col1, col2 = st.columns([8, 1])

if "search" not in st.session_state:
    st.session_state.search = ""

search = col1.text_input(
    "",
    value=st.session_state.search,
    placeholder="Type keyword and press Enter"
)

if col2.button("❌ Clear"):
    st.session_state.search = ""
    st.rerun()

# --------------------------------------------------
# APPLY SEARCH FILTER
# --------------------------------------------------
if search:
    filtered_df = filtered_df[
        filtered_df.apply(
            lambda row: search.lower() in str(row).lower(),
            axis=1
        )
    ]

# --------------------------------------------------
# RESULTS
# --------------------------------------------------
st.markdown(f"### 📄 Results: {len(filtered_df)}")

# Align columns (center except text fields)
def style_table(df):
    return df.style.set_properties(
        subset=[
            "Number", "Priority", "Status",
            "Created Date", "Resolution Date",
            "Release", "Source"
        ],
        **{"text-align": "center"}
    )

st.dataframe(filtered_df, use_container_width=True)

# --------------------------------------------------
# DOWNLOAD BUTTON
# --------------------------------------------------
csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇ Download",
    data=csv,
    file_name="filtered_results.csv",
    mime="text/csv"
)

# --------------------------------------------------
# DATA FRESHNESS
# --------------------------------------------------
if info:
    st.caption(f"🕒 Last refreshed: {info.get('last_refresh')}")
