import streamlit as st
import pandas as pd
import re
import io

from modules.data_loader import load_data
from modules.search import apply_search
from modules.kpi import calculate_kpi

st.set_page_config(layout="wide")

# ================= CSS =================
st.markdown("""
<style>
html, body, [class*="css"]  {
    font-size: 13px !important;
}

[data-testid="stMetricValue"] {
    font-size:14px !important;
}

th, td {
    white-space: nowrap !important;
}

thead th:nth-child(3),
tbody td:nth-child(3) {
    max-width: 400px;
    overflow: hidden;
    text-overflow: ellipsis;
}
</style>
""", unsafe_allow_html=True)

# ================= TITLE =================
st.title("Ops Insight Dashboard")

# ================= LOAD =================
df, last_refresh = load_data()

# ================= SIDEBAR =================
st.sidebar.markdown("## Menu")
st.sidebar.selectbox("", ["Search Tool"])

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

if all_src:
    sources = ["AZURE", "SNOW", "PTC"]
else:
    sources = []
    if azure: sources.append("AZURE")
    if snow: sources.append("SNOW")
    if ptc: sources.append("PTC")

if not sources:
    st.stop()

filtered = df[df["Source"].isin(sources)].copy()

# ================= STATUS =================
st.sidebar.markdown("### Status")
status = st.sidebar.selectbox("", ["ALL"] + sorted(filtered["Status"].dropna().unique()))

# ================= PRIORITY =================
st.sidebar.markdown("### Priority")

def clean_priority(x):
    match = re.search(r"(Severity\s*[1-4]|Priority\s*[1-4])", str(x))
    return match.group(0) if match else str(x)

filtered["Priority"] = filtered["Priority"].apply(clean_priority)

priority = st.sidebar.selectbox("", ["ALL"] + sorted(filtered["Priority"].dropna().unique()))

# ================= APPLY FILTER =================
if status != "ALL":
    filtered = filtered[filtered["Status"] == status]

if priority != "ALL":
    filtered = filtered[filtered["Priority"] == priority]

# ================= SEARCH =================
if "search" not in st.session_state:
    st.session_state.search = ""

col1, col2 = st.columns([10,1])

with col1:
    keyword = st.text_input("🔎 Search", key="search")

with col2:
    if st.button("❌"):
        st.session_state.search = ""
        st.rerun()

filtered = apply_search(filtered, keyword)

# ================= PAGINATION =================
if "page" not in st.session_state:
    st.session_state.page = 1

page_size = 10
total_rows = len(filtered)
total_pages = max(1, (total_rows // page_size) + (1 if total_rows % page_size else 0))

start = (st.session_state.page - 1) * page_size
end = start + page_size
page_df = filtered.iloc[start:end].copy()

page_df.insert(0, "SL No", range(start+1, end+1))

# ================= CLEAN =================
def clean(x):
    return re.sub(r"\s*<.*?>|\(.*?\)", "", str(x)).strip()

for col in ["Created By","Assigned To"]:
    if col in page_df:
        page_df[col] = page_df[col].apply(clean)

for col in ["Created Date","Resolved Date"]:
    if col in page_df:
        page_df[col] = pd.to_datetime(page_df[col], errors="coerce").dt.strftime("%d-%b-%y")

page_df = page_df.fillna("")

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

page_df["Open"] = page_df.apply(lambda r: f'<a href="{build_link(r)}" target="_blank">Open</a>', axis=1)

# ================= RESULTS + PAGINATION (SAME LINE) =================
col1, col2, col3 = st.columns([6,2,2])

with col1:
    st.markdown(f"### Results: {total_rows}")
    c = filtered["Source"].value_counts()
    st.caption(f"AZURE: {c.get('AZURE',0)} | SNOW: {c.get('SNOW',0)} | PTC: {c.get('PTC',0)}"
)

with col2:
    if st.button("◀"):
        if st.session_state.page > 1:
            st.session_state.page -= 1
            st.rerun()

    st.markdown(
        f"<center><b>Page {st.session_state.page} / {total_pages}</b></center>",
        unsafe_allow_html=True
    )

with col3:
    if st.button("▶"):
        if st.session_state.page < total_pages:
            st.session_state.page += 1
            st.rerun()

# ================= EXPORT =================
def convert_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

st.download_button("📥 Download Excel", convert_to_excel(filtered), "ops_data.xlsx")

# ================= TABLE =================
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
