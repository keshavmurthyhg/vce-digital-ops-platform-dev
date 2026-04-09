import math
import streamlit as st
from modules.data_loader import load_data
from modules.filters import apply_filters
from modules.table import show_table


st.set_page_config(layout="wide")

# ================= STYLE =================
st.markdown("""
<style>

/* Table font slightly bigger */
[data-testid="stDataFrame"] {
    font-size: 12px !important;
}

/* Header */
[data-testid="stDataFrame"] th {
    font-size: 12px !important;
}

</style>
""", unsafe_allow_html=True)

# ================= LOAD =================
df, info = load_data()

if df.empty:
    st.stop()

# ================= SIDEBAR =================
with st.sidebar:

    st.markdown("## Ops Insight Dashboard")

    menu = st.selectbox("Menu", ["Search Tool"])

    st.markdown("### Source")

    src_azure = st.checkbox("AZURE", True)
    src_snow = st.checkbox("SNOW", True)
    src_ptc = st.checkbox("PTC", True)

    sources = []
    if src_azure: sources.append("AZURE")
    if src_snow: sources.append("SNOW")
    if src_ptc: sources.append("PTC")

    if not sources:
        st.warning("⚠️ Please select at least one source to view data.")
        st.stop()
    
    st.markdown("### Filters")

    status = st.selectbox("Status", ["ALL"] + sorted(df["Status"].unique()))
    priority = st.selectbox("Priority", ["ALL"] + sorted(df["Priority"].unique()))

# ================= MAIN =================
col1, col2 = st.columns([12,1])

with col1:
    keyword = st.text_input("🔎 Search", key="search")

with col2:
    if st.button("❌"):
        st.session_state.search = ""
        st.rerun()

filtered = apply_filters(df, status, priority, keyword)

filtered = filtered[filtered["Source"].isin(sources)]

# ================= PAGINATION RESET =================
if "page" not in st.session_state:
    st.session_state.page = 1

if st.session_state.get("prev") != (status, priority, tuple(sources), keyword):
    st.session_state.page = 1

st.session_state.prev = (status, priority, tuple(sources), keyword)

# ================= HEADER =================
# ================= HEADER (FIXED ALIGNMENT) =================
col1, col2, col3, col4 = st.columns([6,1,2,1])

total = len(filtered)
import math
total_pages = max(math.ceil(total / page_size), 1)

with col1:
    st.markdown(f"### Results: {total}")

    counts = filtered["Source"].value_counts()
    st.caption(
        f"AZURE: {counts.get('AZURE',0)} | "
        f"SNOW: {counts.get('SNOW',0)} | "
        f"PTC: {counts.get('PTC',0)}"
    )

# ◀ button (left)
with col2:
    prev = st.button("◀")

# Page text (center)
with col3:
    st.markdown(
        f"<div style='text-align:center; margin-top:8px;'>Page {st.session_state.page} / {total_pages}</div>",
        unsafe_allow_html=True
    )

# ▶ button + page size (right)
with col4:
    next_ = st.button("▶")

# rows per page (top right)
page_size = st.selectbox("", [5,10,20], index=1)

if prev and st.session_state.page > 1:
    st.session_state.page -= 1

if next_ and st.session_state.page < total_pages:
    st.session_state.page += 1

# ================= TABLE =================
show_table(filtered, st.session_state.page, page_size)

# ================= KPI =================
with st.sidebar:

    st.markdown("### 📊 KPI")

    total = len(filtered)
    open_ = len(filtered[filtered["Status"].str.lower().str.contains("open")])
    closed = len(filtered[filtered["Status"].str.lower().str.contains("closed")])
    cancelled = len(filtered[filtered["Status"].str.lower().str.contains("cancel")])

    col1, col2 = st.columns(2)
    col1.write(f"Total: {total}")
    col2.write(f"Open: {open_}")
    col1.write(f"Closed: {closed}")
    col2.write(f"Cancelled: {cancelled}")

# ================= FOOTER =================
st.caption(f"Last refreshed: {info}")
