import streamlit as st
import pandas as pd
from modules.data_loader import load_data

st.set_page_config(layout="wide")

# ===================== CSS =====================
st.markdown("""
<style>
.sidebar-section {
    margin-bottom: 10px;
    padding-bottom: 6px;
    border-bottom: 1px solid #ddd;
}
label { font-size: 12px !important; }
div[data-baseweb="select"] { font-size: 12px !important; }
</style>
""", unsafe_allow_html=True)

# ===================== LOAD =====================
df, info = load_data()

# ===================== SIDEBAR =====================
st.sidebar.title("Ops Insight Dashboard")

st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
menu = st.sidebar.selectbox("Menu", ["Search Tool"])
st.sidebar.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
sources = st.sidebar.multiselect(
    "Source",
    ["AZURE", "SNOW", "PTC"],
    default=["AZURE", "SNOW", "PTC"]
)
st.sidebar.markdown('</div>', unsafe_allow_html=True)

# ===================== FILTER =====================
filtered = df[df["Source"].isin(sources)]

status_list = ["ALL"] + sorted(filtered["Status"].unique())
priority_list = ["ALL"] + sorted(filtered["Priority"].unique())

st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
status = st.sidebar.selectbox("Status", status_list)
priority = st.sidebar.selectbox("Priority", priority_list)
st.sidebar.markdown('</div>', unsafe_allow_html=True)

if status != "ALL":
    filtered = filtered[filtered["Status"] == status]

if priority != "ALL":
    filtered = filtered[filtered["Priority"] == priority]

# ===================== SEARCH =====================
col1, col2 = st.columns([10,1])

with col1:
    keyword = st.text_input("🔎 Search", key="search")

with col2:
    if st.button("❌"):
        st.session_state.search = ""
        st.rerun()

if keyword:
    filtered = filtered[
        filtered.apply(lambda row: keyword.lower() in str(row).lower(), axis=1)
    ]

# ===================== KPI =====================
def get_kpi(df):
    status = df["Status"].str.lower()

    total = len(df)
    open_count = status.str.contains("open|progress|new").sum()
    closed = status.str.contains("closed|resolved").sum()
    cancelled = status.str.contains("cancel").sum()

    return total, open_count, closed, cancelled


total, open_count, closed, cancelled = get_kpi(filtered)

# ===================== SIDEBAR KPI =====================
st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
st.sidebar.markdown("### 📊 KPI")
st.sidebar.write(f"Total: {total}")
st.sidebar.write(f"Open: {open_count}")
st.sidebar.write(f"Closed: {closed}")
st.sidebar.write(f"Cancelled: {cancelled}")
st.sidebar.markdown('</div>', unsafe_allow_html=True)

# ===================== RESULT COUNT =====================
st.write(f"### Results: {len(filtered)}")

source_counts = filtered["Source"].value_counts().to_dict()

st.caption(
    f"AZURE: {source_counts.get('AZURE',0)} | "
    f"SNOW: {source_counts.get('SNOW',0)} | "
    f"PTC: {source_counts.get('PTC',0)}"
)

# ===================== PAGINATION =====================
PAGE_SIZE = st.selectbox("Rows per page", [10, 20, 50], index=0)

total_rows = len(filtered)
total_pages = max((total_rows // PAGE_SIZE) + 1, 1)

page = st.number_input("Page", 1, total_pages, 1)

start = (page - 1) * PAGE_SIZE
end = start + PAGE_SIZE

# ===================== TABLE =====================
st.dataframe(
    filtered.iloc[start:end],
    use_container_width=True,
    hide_index=True
)

# ===================== FOOTER =====================
st.caption(f"Last refreshed: {info}")
