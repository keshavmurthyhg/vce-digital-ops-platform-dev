import streamlit as st
from modules.data_loader import load_data
from modules.filters import apply_filters
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

    # --- SOURCE ---
    st.markdown("### Source")
    source = st.radio(
        "",
        ["ALL", "AZURE", "SNOW", "PTC"],
        horizontal=True
    )

    # --- FILTERS ---
    st.markdown("### Filters")

    status = st.selectbox(
        "Status",
        ["ALL"] + sorted(df["Status"].dropna().unique().tolist())
    )

    priority = st.selectbox(
        "Priority",
        ["ALL"] + sorted(df["Priority"].dropna().unique().tolist())
    )

    # --- APPLY FILTERS (INSIDE SIDEBAR FOR KPI) ---
    keyword = st.session_state.get("keyword", "")

    filtered_sidebar = apply_filters(
        df,
        status=status,
        priority=priority,
        keyword=keyword
    )

    if source != "ALL":
        filtered_sidebar = filtered_sidebar[filtered_sidebar["Source"] == source]

    # --- KPI (SIDEBAR) ---
    st.markdown("### 📊 KPI")

    total = len(filtered_sidebar)
    open_ = len(filtered_sidebar[filtered_sidebar["Status"] == "Open"])
    closed = len(filtered_sidebar[filtered_sidebar["Status"] == "Closed"])
    cancelled = len(filtered_sidebar[filtered_sidebar["Status"] == "Cancelled"])

    st.markdown(f"""
    <div style="font-size:12px">
    <b>Total:</b> {total}<br>
    <b>Open:</b> {open_}<br>
    <b>Closed:</b> {closed}<br>
    <b>Cancelled:</b> {cancelled}
    </div>
    """, unsafe_allow_html=True)

# --- MAIN AREA ---

# --- TITLE ---
st.markdown(
    "<h3 style='margin-bottom:10px;'>Ops Insight Dashboard</h3>",
    unsafe_allow_html=True
)

# --- SEARCH ---
keyword = st.text_input("🔎 Search", "", key="keyword")

# --- APPLY FILTERS (MAIN TABLE) ---
filtered = apply_filters(
    df,
    status=status,
    priority=priority,
    keyword=keyword
)

# --- APPLY SOURCE FILTER ---
if source != "ALL":
    filtered = filtered[filtered["Source"] == source]

# --- RESULTS HEADER ---
st.markdown(
    f"<div style='font-size:16px; font-weight:600;'>Results: {len(filtered)}</div>",
    unsafe_allow_html=True
)

# --- TABLE ---
show_table(filtered)

# --- FOOTER ---
if info:
    st.caption(f"Last refreshed: {info.get('last_refresh', '')}")
