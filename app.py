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

/* ===== GLOBAL ===== */
.block-container {
    padding-top: 1rem !important;
}

/* ===== TABLE ===== */
table {
    width: 100%;
    border-collapse: collapse;
}

/* HEADER */
th {
    text-align: center !important;
    padding: 6px !important;
    font-size: 13px;
    background-color: #f5f5f5;
}

/* CELLS */
td {
    padding: 6px !important;
    font-size: 13px;
    white-space: nowrap !important;   /* NO WRAP */
}

/* DESCRIPTION COLUMN */
td:nth-child(3), th:nth-child(3) {
    max-width: 400px;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* PRIORITY COLUMN */
td:nth-child(4), th:nth-child(4) {
    width: 130px;
}

/* DATE COLUMNS */
td:nth-child(7), th:nth-child(7),
td:nth-child(9), th:nth-child(9) {
    min-width: 100px;
}

/* KPI FONT */
[data-testid="stMetricValue"] {
    font-size: 13px !important;
}

/* STATUS COLORS */
.status-open { color: red; font-weight: 600; }
.status-closed { color: green; font-weight: 600; }
.status-cancel { color: gray; font-weight: 600; }

</style>
""", unsafe_allow_html=True)

# ================= TITLE =================
st.title("Ops Insight Dashboard")

# ================= LOAD =================
df, last_refresh = load_data()

# ================= PRIORITY FIX (ONLY PTC) =================
def clean_priority(row):
    val = str(row["Priority"])
    src = row["Source"]

    if src == "PTC":
        m = re.search(r"Severity\s*([1-3])", val)
        return f"Severity {m.group(1)}" if m else ""
    return val

df["Priority"] = df.apply(clean_priority, axis=1)

# ================= SIDEBAR =================
st.sidebar.markdown("## 📊 Menu")
st.sidebar.selectbox("", ["Search Tool"])

# SOURCE
with st.sidebar.expander("📂 Source", True):

    cols = st.columns(2)

    all_src = cols[0].checkbox("ALL", True)
    azure = cols[1].checkbox("AZURE", all_src)
    snow = cols[0].checkbox("SNOW", all_src)
    ptc = cols[1].checkbox("PTC", all_src)

    sources = []
    if all_src:
        sources = ["AZURE", "SNOW", "PTC"]
    else:
        if azure: sources.append("AZURE")
        if snow: sources.append("SNOW")
        if ptc: sources.append("PTC")

    if not sources:
        st.stop()

# ================= BASE FILTER =================
filtered = df[df["Source"].isin(sources)].copy()

# ================= FILTERS =================
with st.sidebar.expander("🎯 Filters", True):

    status = st.multiselect(
        "Status",
        sorted(filtered["Status"].dropna().unique())
    )

    priority = st.multiselect(
        "Priority",
        sorted(filtered["Priority"].dropna().unique())
    )

# APPLY FILTER
if status:
    filtered = filtered[filtered["Status"].isin(status)]

if priority:
    filtered = filtered[filtered["Priority"].isin(priority)]

# ================= SEARCH =================
def clear_search():
    st.session_state.search_box = ""
    st.session_state.page = 1

if "search_box" not in st.session_state:
    st.session_state.search_box = ""

col1, col2 = st.columns([10,1])

with col1:
    st.text_input("🔎 Search", key="search_box")

with col2:
    st.button("❌", on_click=clear_search)

filtered = apply_search(filtered, st.session_state.search_box)

# ================= DATA =================
df_display = filtered.copy().reset_index(drop=True)

# SL NO COLUMN
df_display.insert(0, "SL No", range(1, len(df_display)+1))

# CLEAN TEXT
def clean(x):
    return re.sub(r"\s*<.*?>|\(.*?\)", "", str(x)).strip()

for col in ["Created By","Assigned To"]:
    if col in df_display:
        df_display[col] = df_display[col].apply(clean)

# DATE FORMAT (NO WRAP)
for col in ["Created Date","Resolved Date"]:
    if col in df_display:
        df_display[col] = pd.to_datetime(df_display[col], errors="coerce").dt.strftime("%d-%b-%Y")

# TRUNCATE DESCRIPTION
def truncate_text(x, length=80):
    x = str(x)
    return x[:length] + "..." if len(x) > length else x

df_display["Description"] = df_display["Description"].apply(truncate_text)

df_display = df_display.fillna("")

# STATUS COLOR
def format_status(val):
    v = str(val).lower()
    if "open" in v or "active" in v:
        return f'<span class="status-open">{val}</span>'
    elif "closed" in v:
        return f'<span class="status-closed">{val}</span>'
    elif "cancel" in v:
        return f'<span class="status-cancel">{val}</span>'
    return val

df_display["Status"] = df_display["Status"].apply(format_status)

# LINK
def make_link(row):
    num = str(row["Number"])
    src = row["Source"]

    if src == "SNOW":
        url = f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={num}"
    elif src == "PTC":
        url = f"https://support.ptc.com/appserver/cs/view/case.jsp?n={num}"
    elif src == "AZURE":
        url = f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{num}"
    else:
        url = ""

    return f'<a href="{url}" target="_blank">Open</a>' if url else ""

df_display["Open"] = df_display.apply(make_link, axis=1)

# ================= PAGINATION =================
#if "page" not in st.session_state:
 #   st.session_state.page = 1

#page_size = 10
#total_rows = len(df_display)
#total_pages = max(1, (total_rows // page_size) + (1 if total_rows % page_size else 0))

#start = (st.session_state.page - 1) * page_size
#end = start + page_size
#page_df = df_display.iloc[start:end]

# ================= PAGINATION (NEW) =================

col1, col2, col3 = st.columns([2,2,6])

with col1:
    page_size = st.selectbox(
        "Rows",
        [10, 20, 50, 100],
        index=0
    )

total_rows = len(df_display)
total_pages = max(1, (total_rows // page_size) + (1 if total_rows % page_size else 0))

with col2:
    page = st.selectbox(
        "Page",
        list(range(1, total_pages + 1))
    )

start = (page - 1) * page_size
end = start + page_size

page_df = df_display.iloc[start:end]

# ================= HEADER =================
colA, colB, colC = st.columns([4,3,3])

with colA:
    st.markdown(f"**Results: {total_rows}**")
    vc = filtered["Source"].value_counts()
    st.caption(f"AZURE: {vc.get('AZURE',0)} | SNOW: {vc.get('SNOW',0)} | PTC: {vc.get('PTC',0)}")

with colB:
    def to_excel(df):
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        return buffer.getvalue()

    st.download_button("📥 Download Excel", to_excel(filtered), "ops_data.xlsx")

#with colC:
 #   c1, c2, c3 = st.columns([1,2,1])

  #  if c1.button("◀") and st.session_state.page > 1:
  #      st.session_state.page -= 1
  #      st.rerun()

   # c2.markdown(f"<div style='text-align:center;'>Page {st.session_state.page}/{total_pages}</div>", unsafe_allow_html=True)

  #  if c3.button("▶") and st.session_state.page < total_pages:
    #    st.session_state.page += 1
     #   st.rerun()

# ================= TABLE =================
st.write(page_df.to_html(escape=False, index=False), unsafe_allow_html=True)

# ================= KPI =================
with st.sidebar.expander("📈 KPI", True):

    kpi = calculate_kpi(filtered)

    c1,c2 = st.columns(2)
    c1.metric("Total", kpi["total"])
    c2.metric("Open", kpi["open"])

    c3,c4 = st.columns(2)
    c3.metric("Closed", kpi["closed"])
    c4.metric("Cancelled", kpi["cancelled"])

# ================= REFRESH =================
st.caption(f"Last refreshed: {last_refresh}")
