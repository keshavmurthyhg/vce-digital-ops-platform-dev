import streamlit as st
import pandas as pd
import re

from modules.data_loader import load_data
from modules.search import apply_search
from modules.kpi import calculate_kpi

st.set_page_config(layout="wide")

# ================= UI =================
st.markdown("""
<style>
html, body, [class*="css"]  {
    font-size: 13px !important;
}
table {font-size: 12px !important;}

.block-container {
    padding-top: 1rem;
}

section[data-testid="stSidebar"] > div {
    padding-top: 10px;
}

/* FULL WIDTH SEARCH */
div[data-testid="stTextInput"] > div {
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ================= TITLE =================
st.title("Ops Insight Dashboard")

# ================= LOAD =================
df, last_refresh = load_data()

# ================= SESSION =================
if "page" not in st.session_state:
    st.session_state.page = 1

# ================= SIDEBAR =================
st.sidebar.markdown("## Menu")

menu = st.sidebar.selectbox(
    "",
    ["Search Tool", "Matrix Board (Coming)", "Dashboards (Coming)"]
)

st.sidebar.markdown("---")

# ================= SOURCE =================
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
    st.stop()

st.sidebar.markdown("---")

# ================= FILTER BASE =================
filtered = df[df["Source"].isin(sources)].copy()

# ================= STATUS =================
st.sidebar.markdown("### Status")
status_list = ["ALL"] + sorted(filtered["Status"].dropna().unique())
status = st.sidebar.selectbox("", status_list)

# ================= PRIORITY =================
st.sidebar.markdown("### Priority")

# FIXED PRIORITY CLEANING (DO NOT REMOVE FULL TEXT)
def extract_severity(x):
    match = re.search(r"Severity\s*[1-4]", str(x))
    return match.group(0) if match else str(x)

filtered["Priority"] = filtered["Priority"].apply(extract_severity)

priority_list = ["ALL"] + sorted(filtered["Priority"].dropna().unique())
priority = st.sidebar.selectbox("", priority_list)

# ================= RELEASE (OPTIONAL) =================
release = "ALL"
if "Release" in filtered.columns and "AZURE" in sources:
    st.sidebar.markdown("### Release")
    rel_list = ["ALL"] + sorted(filtered["Release"].dropna().unique())
    release = st.sidebar.selectbox("", rel_list)

st.sidebar.markdown("---")

# ================= APPLY FILTER =================
if status != "ALL":
    filtered = filtered[filtered["Status"] == status]

if priority != "ALL":
    filtered = filtered[filtered["Priority"] == priority]

if release != "ALL":
    filtered = filtered[filtered["Release"] == release]

# ================= SEARCH =================
col1, col2 = st.columns([12,1])

with col1:
    keyword = st.text_input("🔎 Search", key="search")

with col2:
    if st.button("❌"):
        st.session_state.pop("search", None)
        st.rerun()

filtered = apply_search(filtered, keyword)

# ================= PAGINATION =================
total = len(filtered)
page_size = 10
total_pages = max((total + page_size - 1)//page_size,1)

c1, c2, c3 = st.columns([6,1,1])

with c1:
    st.markdown(f"### Results: {total}")
    c = filtered["Source"].value_counts()
    st.caption(f"AZURE: {c.get('AZURE',0)} | SNOW: {c.get('SNOW',0)} | PTC: {c.get('PTC',0)}")

with c2:
    prev = st.button("◀")

# CENTER PAGE NUMBER
st.markdown(
    f"<div style='text-align:center;'>Page {st.session_state.page} / {total_pages}</div>",
    unsafe_allow_html=True
)

if prev and st.session_state.page > 1:
    st.session_state.page -= 1

if next and st.session_state.page < total_pages:
    st.session_state.page += 1

with c3:
    next = st.button("▶")
# ================= DATA =================
start = (st.session_state.page-1)*page_size
end = start+page_size

page_df = filtered.iloc[start:end].copy().reset_index(drop=True)
page_df.insert(0,"SL No", range(start+1,start+len(page_df)+1))

# CLEAN TEXT
def clean(x):
    return re.sub(r"\s*<.*?>|\(.*?\)", "", str(x)).strip()

for col in ["Created By","Assigned To"]:
    if col in page_df:
        page_df[col] = page_df[col].apply(clean)

# DATE FORMAT
for col in ["Created Date","Resolved Date"]:
    if col in page_df:
        page_df[col] = pd.to_datetime(page_df[col], errors="coerce").dt.strftime("%d-%b-%y")

# REMOVE NONE
page_df = page_df.replace("None", "").fillna("")

# ================= LINK =================
def build_link(row):
    num = str(row["Number"])
    src = row["Source"]

    if src == "SNOW":
        return f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={num}"
    elif src == "PTC":
        return f"https://support.ptc.com/appserver/cs/view/case.jsp?n={num}"
    elif src == "AZURE":
        return f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{num}"
    return ""

page_df["Open"] = page_df.apply(
    lambda r: f'<a href="{build_link(r)}" target="_blank">Open</a>', axis=1
)

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
