import streamlit as st
from modules.data_loader import load_data
from modules.filters import apply_filters
from modules.table import show_table

st.set_page_config(layout="wide")

# --- STYLE (compact UI) ---
st.markdown("""
<style>
section[data-testid="stSidebar"] { font-size: 13px; }
.stRadio label { font-size: 12px !important; }
.stSelectbox div[data-baseweb="select"] { min-height: 30px !important; }
</style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
df, info = load_data()

if df.empty:
    st.error("No data loaded")
    st.stop()

# =========================
# SIDEBAR (MENU + KPI)
# =========================
with st.sidebar:

    st.markdown("## Ops Insight Dashboard")

    # --- MENU ---
    menu = st.selectbox("Menu", ["Search Tool"])

    # --- SOURCE ---
    st.markdown("### Source")
    source = st.radio("", ["ALL", "AZURE", "SNOW", "PTC"], horizontal=True)

    # --- FILTERS ---
    st.markdown("### Filters")

    status = st.selectbox(
        "Status",
        ["ALL"] + sorted(df["Status"].dropna().unique())
    )

    priority = st.selectbox(
        "Priority",
        ["ALL"] + sorted(df["Priority"].dropna().unique())
    )

# =========================
# MAIN AREA
# =========================

st.markdown("### Ops Insight Dashboard")

keyword = st.text_input("🔎 Search")

# --- APPLY FILTERS ---
filtered = apply_filters(df, status, priority, keyword)

# --- SOURCE FILTER ---
if source != "ALL":
    filtered = filtered[filtered["Source"] == source]

# --- RESULTS ---
st.markdown(f"**Results: {len(filtered)}**")

# --- TABLE ---
show_table(filtered)

# =========================
# KPI (SIDEBAR BOTTOM)
# =========================
with st.sidebar:

    st.markdown("### 📊 KPI")

    total = len(filtered)
    open_ = len(filtered[filtered["Status"] == "Open"])
    closed = len(filtered[filtered["Status"] == "Closed"])
    cancelled = len(filtered[filtered["Status"] == "Cancelled"])

    st.markdown(f"""
    <div style="font-size:12px">
    <b>Total:</b> {total}<br>
    <b>Open:</b> {open_}<br>
    <b>Closed:</b> {closed}<br>
    <b>Cancelled:</b> {cancelled}
    </div>
    """, unsafe_allow_html=True)

# --- FOOTER ---
if info:
    st.caption(f"Last refreshed: {info}")
