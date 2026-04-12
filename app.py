import streamlit as st
import pandas as pd
import re
import io

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from modules.data_loader import load_data
from modules.search import apply_search
from modules.kpi import calculate_kpi

st.set_page_config(layout="wide")

# ================= UI =================
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
}

html, body, [class*="css"]  {
    font-size: 13px !important;
}

[data-testid="stMetricValue"] {
    font-size:14px !important;
}
</style>
""", unsafe_allow_html=True)

# ================= TITLE =================
st.title("Ops Insight Dashboard")

# ================= LOAD =================
df, last_refresh = load_data()

# ================= SIDEBAR =================
st.sidebar.markdown("## Menu")
menu = st.sidebar.selectbox("", ["Search Tool", "Matrix Board (Coming)", "Dashboards (Coming)"])

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

# FIX ALL
if all_src:
    sources = ["AZURE", "SNOW", "PTC"]
else:
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

def clean_priority(x):
    match = re.search(r"(Severity\s*[1-4]|Priority\s*[1-4])", str(x))
    return match.group(0) if match else str(x)

filtered["Priority"] = filtered["Priority"].apply(clean_priority)

priority_list = ["ALL"] + sorted(filtered["Priority"].dropna().unique())
priority = st.sidebar.selectbox("", priority_list)

st.sidebar.markdown("---")

# ================= APPLY FILTER =================
if status != "ALL":
    filtered = filtered[filtered["Status"] == status]

if priority != "ALL":
    filtered = filtered[filtered["Priority"] == priority]

# ================= SEARCH =================
col1, col2 = st.columns([10,1])

with col1:
    keyword = st.text_input(
    "🔎 Search",
    value=st.session_state.get("search", ""),
    key="search"
)

with col2:
    if st.button("❌"):
    st.session_state.pop("search", None)
    st.rerun()

filtered = apply_search(filtered, keyword)

# ================= RESULTS =================
st.markdown(f"### Results: {len(filtered)}")

c = filtered["Source"].value_counts()
st.caption(
    f"AZURE: {c.get('AZURE',0)} | "
    f"SNOW: {c.get('SNOW',0)} | "
    f"PTC: {c.get('PTC',0)}"
)

# ================= DATA CLEAN =================
page_df = filtered.copy().reset_index(drop=True)
page_df.insert(0, "SL No", range(1, len(page_df)+1))

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

page_df["Open"] = page_df.apply(build_link, axis=1)

# ================= EXPORT =================
def convert_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

st.download_button(
    "📥 Download Excel",
    data=convert_to_excel(filtered),
    file_name="ops_data.xlsx"
)

# ================= Result Count =================
st.markdown(f"### Results: {len(filtered)}")

c = filtered["Source"].value_counts()
st.caption(
    f"AZURE: {c.get('AZURE',0)} | "
    f"SNOW: {c.get('SNOW',0)} | "
    f"PTC: {c.get('PTC',0)}"
)

# ================= AG GRID =================
from st_aggrid import AgGrid, GridOptionsBuilder

# REMOVE EXTRA COLUMN BUG
if "__auto_unique_id__" in page_df.columns:
    page_df = page_df.drop(columns=["__auto_unique_id__"])

# GRID BUILDER
gb = GridOptionsBuilder.from_dataframe(page_df)

gb.configure_default_column(
    sortable=True,
    filter=True,
    resizable=True
)

# DESCRIPTION WIDTH
gb.configure_column("Description", width=400)

# OPEN LINK
gb.configure_column(
    "Open",
    cellRenderer='''
    function(params) {
        if (params.value) {
            return `<a href="${params.value}" target="_blank">Open</a>`
        } else {
            return ""
        }
    }
    '''
)

# ✅ IMPORTANT: ENABLE PAGINATION
gb.configure_pagination(
    enabled=True,
    paginationAutoPageSize=False,
    paginationPageSize=10
)

grid_options = gb.build()

AgGrid(
    page_df,
    gridOptions=grid_options,
    height=500,  # 🔥 REQUIRED (without this grid disappears)
    fit_columns_on_grid_load=True,
    theme="streamlit"
)

# ================= Download to excel =================

def convert_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

st.download_button(
    "📥 Download Excel",
    convert_to_excel(filtered),
    "ops_data.xlsx"
)

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
