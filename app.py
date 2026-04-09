import streamlit as st
import pandas as pd
from modules.data_loader import load_data

st.set_page_config(layout="wide")

# ================= CSS =================
st.markdown("""
<style>

/* Sidebar compact */
.sidebar-section {
    margin-bottom: 6px;
    padding-bottom: 4px;
    border-bottom: 1px solid #ddd;
}

/* Smaller fonts */
label { font-size: 11px !important; }
div[data-baseweb="select"] { font-size: 11px !important; }

/* Reduce padding */
.block-container { padding-top: 1rem; }

/* KPI grid */
.kpi-box {
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)

# ================= LOAD =================
df, refresh_time = load_data()

# ================= SIDEBAR =================
st.sidebar.title("Ops Insight Dashboard")

st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
menu = st.sidebar.selectbox("Menu", ["Search Tool"])
st.sidebar.markdown('</div>', unsafe_allow_html=True)

# ✅ CHECKBOX SOURCE (FIXED)
st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)

src_azure = st.sidebar.checkbox("AZURE", True)
src_snow = st.sidebar.checkbox("SNOW", True)
src_ptc = st.sidebar.checkbox("PTC", True)

sources = []
if src_azure: sources.append("AZURE")
if src_snow: sources.append("SNOW")
if src_ptc: sources.append("PTC")

st.sidebar.markdown('</div>', unsafe_allow_html=True)

filtered = df[df["Source"].isin(sources)]

# ================= FILTER =================
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

# ================= SEARCH =================
col1, col2 = st.columns([10,1])

with col1:
    keyword = st.text_input("🔎 Search", key="search")

with col2:
    if st.button("❌"):
        st.session_state.search = ""
        st.rerun()

if keyword:
    filtered = filtered[
        filtered.apply(lambda r: keyword.lower() in str(r).lower(), axis=1)
    ]

# ================= KPI =================
status_col = filtered["Status"].str.lower()

total = len(filtered)
open_count = status_col.str.contains("open|new|progress").sum()
closed = status_col.str.contains("closed|resolved").sum()
cancelled = status_col.str.contains("cancel").sum()

# ✅ 2 COLUMN KPI
st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
st.sidebar.markdown("### 📊 KPI")

col1, col2 = st.sidebar.columns(2)
col1.write(f"Total: {total}")
col2.write(f"Open: {open_count}")

col1.write(f"Closed: {closed}")
col2.write(f"Cancelled: {cancelled}")

st.sidebar.markdown('</div>', unsafe_allow_html=True)

# ================= RESULT HEADER =================
c1, c2 = st.columns([6,2])

with c1:
    st.markdown(f"### Results: {total}")

    counts = filtered["Source"].value_counts()
    st.caption(
        f"AZURE: {counts.get('AZURE',0)} | "
        f"SNOW: {counts.get('SNOW',0)} | "
        f"PTC: {counts.get('PTC',0)}"
    )

# ================= PAGINATION INLINE =================
with c2:
    page_size = st.selectbox("", [10,20,50], index=0)

total_pages = max((total // page_size) + 1, 1)

p1, p2, p3 = st.columns([1,2,1])

with p1:
    prev = st.button("◀")

with p2:
    page = st.session_state.get("page", 1)
    st.markdown(f"**Page {page} / {total_pages}**")

with p3:
    next_ = st.button("▶")

if prev and page > 1:
    page -= 1
if next_ and page < total_pages:
    page += 1

st.session_state.page = page

start = (page - 1) * page_size
end = start + page_size

# ================= TABLE =================
show_df = filtered.iloc[start:end].copy()

# ✅ CLICKABLE LINK
show_df["Link"] = show_df.apply(
    lambda x: f"[Open]({x['Link']})" if x["Link"] else "",
    axis=1
)

st.dataframe(show_df, use_container_width=True, hide_index=True)

# ================= FOOTER =================
st.caption(f"Last refreshed: {refresh_time}")
