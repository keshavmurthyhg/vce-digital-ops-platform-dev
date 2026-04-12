import streamlit as st
import pandas as pd
import re

from modules.data_loader import load_data
from modules.filters import apply_filters
from modules.search import apply_search
from modules.kpi import calculate_kpi

st.set_page_config(layout="wide")

# ================= CSS (UI CONTROL) =================
st.markdown("""
<style>
/* Reduce sidebar spacing */
section[data-testid="stSidebar"] > div {
    padding-top: 10px;
}

/* Smaller KPI font */
[data-testid="stMetricValue"] {
    font-size: 18px;
}
[data-testid="stMetricLabel"] {
    font-size: 12px;
}

/* Reduce search width */
div[data-testid="stTextInput"] > div {
    width: 50%;
}

/* Sticky header */
thead tr th {
    position: sticky;
    top: 0;
    background: white;
    z-index: 1;
}

/* Table font */
table {
    font-size: 13px !important;
}
</style>
""", unsafe_allow_html=True)

# ================= LOAD =================
df, last_refresh = load_data()

# ================= SESSION =================
if "page" not in st.session_state:
    st.session_state.page = 1
if "search" not in st.session_state:
    st.session_state.search = ""

# ================= SIDEBAR =================
st.sidebar.title("Ops Insight Dashboard")

st.sidebar.markdown("### Source")

col1, col2 = st.sidebar.columns(2)

with col1:
    all_src = st.checkbox("ALL", value=True)

with col2:
    azure = st.checkbox("AZURE", value=all_src)
    snow = st.checkbox("SNOW", value=all_src)
    ptc = st.checkbox("PTC", value=all_src)

sources = []
if azure: sources.append("AZURE")
if snow: sources.append("SNOW")
if ptc: sources.append("PTC")

if not sources:
    st.warning("⚠️ Select at least one source")
    st.stop()

# ================= FILTERS =================
filtered = df[df["Source"].isin(sources)]

# Dynamic label
priority_label = "Release" if sources == ["AZURE"] else "Priority"

st.sidebar.markdown("### Status")
status_list = ["ALL"] + sorted(filtered["Status"].dropna().unique())
status = st.sidebar.selectbox("", status_list)

st.sidebar.markdown(f"### {priority_label}")
priority_list = ["ALL"] + sorted(filtered["Priority"].dropna().unique())
priority = st.sidebar.selectbox("", priority_list)

filtered = apply_filters(filtered, status, priority)

# ================= SEARCH =================
col1, col2 = st.columns([5,1])

with col1:
    keyword = st.text_input("🔎 Search", key="search")

with col2:
    if st.button("❌ Clear"):
        st.session_state.search = ""
        st.rerun()

filtered = apply_search(filtered, keyword)

# ================= PAGINATION =================
total = len(filtered)
page_size = 10
total_pages = max((total + page_size - 1)//page_size,1)

col1, col2, col3 = st.columns([6,1,2])

with col1:
    st.markdown(f"### Results: {total}")

with col2:
    if st.button("◀") and st.session_state.page > 1:
        st.session_state.page -= 1

with col3:
    if st.button("▶") and st.session_state.page < total_pages:
        st.session_state.page += 1

st.markdown(
    f"<div style='text-align:center;'>Page {st.session_state.page} / {total_pages}</div>",
    unsafe_allow_html=True
)

# ================= DATA =================
start = (st.session_state.page-1)*page_size
end = start+page_size

page_df = filtered.iloc[start:end].copy().reset_index(drop=True)
page_df.insert(0,"SL No", range(start+1,start+len(page_df)+1))

# CLEAN
def clean(x):
    return re.sub(r"\s*<.*?>|\(.*?\)", "", str(x)).strip()

for col in ["Created By","Assigned To"]:
    if col in page_df:
        page_df[col] = page_df[col].apply(clean)

for col in ["Created Date","Resolved Date"]:
    if col in page_df:
        page_df[col] = pd.to_datetime(page_df[col], errors="coerce").dt.strftime("%d-%b-%y")

# LINK
def build_link(row):
    num = str(row.get("Number", ""))
    src = row.get("Source", "")

    if src == "SNOW":
        return f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={num}"
    elif src == "PTC":
        return f"https://support.ptc.com/appserver/cs/view/case.jsp?n={num}"
    elif src == "AZURE":
        return f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{num}"
    return ""

page_df["URL"] = page_df.apply(build_link, axis=1)

# ================= DISPLAY =================
event = st.dataframe(
    page_df,
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row",
    column_config={
        "Description": st.column_config.TextColumn(width="large"),
    }
)

# ================= CLICKABLE ROW =================
if event.selection.rows:
    row = page_df.iloc[event.selection.rows[0]]
    if row["URL"]:
        st.link_button("🔍 Open Ticket", row["URL"])

# ================= KPI =================
st.sidebar.markdown("### KPI")

kpi = calculate_kpi(filtered)

c1,c2 = st.sidebar.columns(2)
c1.metric("Total", kpi["total"])
c2.metric("Open", kpi["open"])

c3,c4 = st.sidebar.columns(2)
c3.metric("Closed", kpi["closed"])
c4.metric("Cancelled", kpi["cancelled"])

# ================= REFRESH =================
st.caption(f"Last refreshed: {last_refresh}")
