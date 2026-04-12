import streamlit as st
import pandas as pd
import re

from modules.data_loader import load_data
from modules.filters import apply_filters
from modules.search import apply_search
from modules.kpi import calculate_kpi

st.set_page_config(layout="wide")

# ================= CSS =================
st.markdown("""
<style>
section[data-testid="stSidebar"] > div {
    padding-top: 10px;
}

[data-testid="stMetricValue"] {font-size:18px;}
[data-testid="stMetricLabel"] {font-size:12px;}

div[data-testid="stTextInput"] > div {
    width: 50%;
}
</style>
""", unsafe_allow_html=True)

# ================= LOAD =================
df, last_refresh = load_data()

# ================= SESSION =================
if "page" not in st.session_state:
    st.session_state.page = 1

# ================= SIDEBAR =================
st.sidebar.title("Ops Insight Dashboard")

# MENU
st.sidebar.markdown("### Menu")
st.sidebar.caption("Filters & Controls")

# SOURCE
st.sidebar.markdown("### Source")
c1, c2 = st.sidebar.columns(2)

with c1:
    all_src = st.checkbox("ALL", value=True)

with c2:
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

# STATUS
st.sidebar.markdown("### Status")
status_list = ["ALL"] + sorted(filtered["Status"].dropna().unique())
status = st.sidebar.selectbox("", status_list)

# PRIORITY
st.sidebar.markdown("### Priority")

if sources == ["PTC"]:
    priority_list = ["ALL", "Severity 1", "Severity 2", "Severity 3"]
else:
    priority_list = ["ALL"] + sorted(filtered["Priority"].dropna().unique())

priority = st.sidebar.selectbox("", priority_list)

# RELEASE (dynamic)
release = "ALL"
if "AZURE" in sources and "Release" in filtered.columns:
    st.sidebar.markdown("### Release")
    release_list = ["ALL"] + sorted(filtered["Release"].dropna().unique())
    release = st.sidebar.selectbox("", release_list)

# APPLY FILTERS
filtered = apply_filters(filtered, status, priority)

if release != "ALL" and "Release" in filtered.columns:
    filtered = filtered[filtered["Release"] == release]

# ================= SEARCH =================
col1, col2 = st.columns([10,1])

with col1:
    keyword = st.text_input("🔎 Search", key="search")

with col2:
    if st.button("❌", help="Clear search"):
        st.session_state.pop("search", None)
        st.rerun()

filtered = apply_search(filtered, keyword)

# ================= PAGINATION =================
total = len(filtered)
page_size = 10
total_pages = max((total + page_size - 1)//page_size,1)

col1, col2, col3 = st.columns([6,1,1])

with col1:
    st.markdown(f"### Results: {total}")

    c = filtered["Source"].value_counts()
    st.caption(
        f"AZURE: {c.get('AZURE',0)} | "
        f"SNOW: {c.get('SNOW',0)} | "
        f"PTC: {c.get('PTC',0)}"
    )

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

# DATE FORMAT
for col in ["Created Date","Resolved Date"]:
    if col in page_df:
        page_df[col] = pd.to_datetime(page_df[col], errors="coerce").dt.strftime("%d-%b-%y")

# REMOVE None
page_df = page_df.replace("None", "").fillna("")

# CLEAN PRIORITY (PTC)
def clean_priority(row):
    if row["Source"] == "PTC":
        match = re.search(r"Severity\s*[1-4]", str(row["Priority"]))
        return match.group(0) if match else row["Priority"]
    return row["Priority"]

page_df["Priority"] = page_df.apply(clean_priority, axis=1)

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

# OPEN COLUMN
def make_open(row):
    url = build_link(row)
    if not url:
        return ""
    return f'<a href="{url}" target="_blank">Open</a>'

page_df["Open"] = page_df.apply(make_open, axis=1)

# ================= DISPLAY =================
st.write(page_df.to_html(escape=False, index=False), unsafe_allow_html=True)

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
