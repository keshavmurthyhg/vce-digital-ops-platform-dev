import streamlit as st
import pandas as pd

from modules.data_loader import load_data
from modules.filters import apply_filters
from modules.search import apply_search
from modules.kpi import calculate_kpi

# ================= CONFIG =================
st.set_page_config(layout="wide")

# ================= LOAD DATA =================
df, info = load_data()

# ================= SESSION =================
if "page" not in st.session_state:
    st.session_state.page = 1

# ================= SIDEBAR =================
st.sidebar.title("Ops Insight Dashboard")

st.sidebar.markdown("### Menu")
menu = st.sidebar.selectbox("", ["Search Tool"])

# -------- SOURCE (CHECKBOX) --------
st.sidebar.markdown("### Source")

azure_selected = st.sidebar.checkbox("AZURE")
snow_selected = st.sidebar.checkbox("SNOW")
ptc_selected = st.sidebar.checkbox("PTC")

sources = []
if azure_selected:
    sources.append("AZURE")
if snow_selected:
    sources.append("SNOW")
if ptc_selected:
    sources.append("PTC")

# ✅ NO SOURCE SELECTED
if not sources:
    st.warning("⚠️ Please select at least one source to view data.")
    st.stop()

# ================= FILTERS =================
st.sidebar.markdown("### Filters")

status = st.sidebar.selectbox("Status", ["ALL"] + sorted(df["Status"].dropna().unique()))
priority = st.sidebar.selectbox("Priority", ["ALL"] + sorted(df["Priority"].dropna().unique()))

# ================= SEARCH =================
col1, col2, col3 = st.columns([4,1,7])

with col1:
    keyword = st.text_input("🔎 Search", key="search")

with col2:
    if st.button("❌"):
        st.session_state.search = ""
        st.rerun()

# ================= FILTER DATA =================
filtered = df[df["Source"].isin(sources)]

filtered = apply_filters(filtered, status, priority)
filtered = apply_search(filtered, keyword)

# ================= RESET PAGE ON FILTER CHANGE =================
if "prev_filter" not in st.session_state:
    st.session_state.prev_filter = ""

current_filter = str(sources) + str(status) + str(priority) + str(keyword)

if current_filter != st.session_state.prev_filter:
    st.session_state.page = 1
    st.session_state.prev_filter = current_filter

# ================= PAGINATION =================
total = len(filtered)

page_size = st.selectbox("", [5, 10, 20], index=1)

total_pages = max((total + page_size - 1) // page_size, 1)

# ================= HEADER =================
col1, col2, col3, col4 = st.columns([5,1,2,2])

with col1:
    st.markdown(f"<h5>Results: {total}</h5>", unsafe_allow_html=True)

    counts = filtered["Source"].value_counts()
    st.caption(
        f"AZURE: {counts.get('AZURE',0)} | "
        f"SNOW: {counts.get('SNOW',0)} | "
        f"PTC: {counts.get('PTC',0)}"
    )

with col2:
    prev_btn = st.button("◀")

with col3:
    st.markdown(
        f"<div style='text-align:center;margin-top:6px;'>Page {st.session_state.page} / {total_pages}</div>",
        unsafe_allow_html=True
    )

with col4:
    next_btn = st.button("▶")
    page_size = st.selectbox("", [5,10,20], index=1)

# ================= PAGE NAVIGATION =================
if prev_btn and st.session_state.page > 1:
    st.session_state.page -= 1

if next_btn and st.session_state.page < total_pages:
    st.session_state.page += 1

# ================= SLICE DATA =================
start = (st.session_state.page - 1) * page_size
end = start + page_size

page_df = filtered.iloc[start:end].copy()

# ================= FORMAT =================
page_df.insert(0, "SL No", range(start+1, start+len(page_df)+1))

# DATE FORMAT
for col in ["Created Date", "Resolved Date"]:
    if col in page_df.columns:
        page_df[col] = pd.to_datetime(page_df[col], errors="coerce").dt.strftime("%d-%b-%y")

# LINK COLUMN
if "Number" in page_df.columns:
    page_df["Link"] = page_df["Number"].apply(
        lambda x: f"https://support.ptc.com/appserver/cs/view/case.jsp?n={x}"
        if pd.notna(x) else ""
    )

# ================= DISPLAY =================
st.dataframe(page_df, use_container_width=True, hide_index=True)

# ================= KPI =================
st.sidebar.markdown("### 📊 KPI")

kpi = calculate_kpi(filtered)

col1, col2 = st.sidebar.columns(2)
col1.metric("Total", kpi["total"])
col2.metric("Open", kpi["open"])

col3, col4 = st.sidebar.columns(2)
col3.metric("Closed", kpi["closed"])
col4.metric("Cancelled", kpi["cancelled"])

# ================= LAST REFRESH =================
st.caption(f"Last refreshed: {info}")
