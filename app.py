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

/* GLOBAL */
.block-container {padding-top: 1rem;}

html, body, [class*="css"] {
    font-size: 13px !important;
}

/* KPI */
[data-testid="stMetricValue"] {
    font-size:14px !important;
}

/* TABLE */
table {
    border-collapse: collapse;
    width: 100%;
}

th {
    text-align: center !important;
    background-color: #f5f5f5;
    font-weight: 600;
}

td {
    text-align: left;
    padding: 6px;
    white-space: nowrap;
}

tr:hover {
    background-color: #f9f9f9;
}

/* DESCRIPTION COLUMN */
td:nth-child(3), th:nth-child(3) {
    max-width: 400px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* LINKS */
a {
    text-decoration: none;
    color: #1f77b4;
    font-weight: 500;
}

/* SIDEBAR COMPACT */
section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] > div {
    gap: 0.3rem !important;
}

section[data-testid="stSidebar"] label {
    margin-bottom: 2px !important;
}

section[data-testid="stSidebar"] .stSelectbox,
section[data-testid="stSidebar"] .stCheckbox {
    margin-bottom: 4px !important;
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

st.sidebar.markdown("---")

# ================= FILTER =================
filtered = df[df["Source"].isin(sources)].copy()

# STATUS
st.sidebar.markdown("### Status")
status_list = ["ALL"] + sorted(filtered["Status"].dropna().unique())
status = st.sidebar.selectbox("", status_list)

# PRIORITY
st.sidebar.markdown("### Priority")

def clean_priority(x):
    m = re.search(r"(Severity\s*[1-4]|Priority\s*[1-4])", str(x))
    return m.group(0) if m else str(x)

filtered["Priority"] = filtered["Priority"].apply(clean_priority)

priority_list = ["ALL"] + sorted(filtered["Priority"].dropna().unique())
priority = st.sidebar.selectbox("", priority_list)

st.sidebar.markdown("---")

# APPLY FILTER
if status != "ALL":
    filtered = filtered[filtered["Status"] == status]

if priority != "ALL":
    filtered = filtered[filtered["Priority"] == priority]

# ================= SEARCH =================
#if "search_box" not in st.session_state:
  #  st.session_state.search_box = ""

#col1, col2 = st.columns([10,1])
#
#with col1:
#    keyword = st.text_input(
 #       "🔎 Search",
  #      key="search_box"
#    )

#with col2:
   # if st.button("❌"):
  #     st.session_state.search_box = ""
   #     st.session_state.page = 1
   #     st.rerun()

#filtered = apply_search(filtered, st.session_state.search_box)

# ================= SEARCH =================
def clear_search():
    st.session_state["search_box"] = ""
    st.session_state["page"] = 1

if "search_box" not in st.session_state:
    st.session_state["search_box"] = ""

col1, col2 = st.columns([10,1])

with col1:
    keyword = st.text_input(
        "🔎 Search",
        key="search_box"
    )

with col2:
    st.button("❌", on_click=clear_search)

filtered = apply_search(filtered, st.session_state["search_box"])


# ================= DATA =================
df_display = filtered.copy().reset_index(drop=True)
df_display.insert(0, "SL No", range(1, len(df_display)+1))

# CLEAN TEXT
def clean(x):
    return re.sub(r"\s*<.*?>|\(.*?\)", "", str(x)).strip()

for col in ["Created By","Assigned To"]:
    if col in df_display:
        df_display[col] = df_display[col].apply(clean)

# DATE FORMAT
for col in ["Created Date","Resolved Date"]:
    if col in df_display:
        df_display[col] = pd.to_datetime(df_display[col], errors="coerce").dt.strftime("%d-%b-%y")

df_display = df_display.fillna("")

# ================= LINK =================
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
if "page" not in st.session_state:
    st.session_state.page = 1

page_size = 10
total_rows = len(df_display)
total_pages = max(1, (total_rows // page_size) + (1 if total_rows % page_size else 0))

start = (st.session_state.page - 1) * page_size
end = start + page_size
page_df = df_display.iloc[start:end]

# ================= HEADER ROW =================
colA, colB, colC = st.columns([4,3,3])

with colA:
    st.markdown(
        f"<div style='font-size:16px; font-weight:600;'>Results: {total_rows}</div>",
        unsafe_allow_html=True
    )

    vc = filtered["Source"].value_counts()
    st.caption(
        f"AZURE: {vc.get('AZURE',0)} | "
        f"SNOW: {vc.get('SNOW',0)} | "
        f"PTC: {vc.get('PTC',0)}"
    )

with colB:
    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)

    def to_excel(df):
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        return buffer.getvalue()

    st.download_button("📥 Download Excel", to_excel(filtered), "ops_data.xlsx")

    st.markdown("</div>", unsafe_allow_html=True)

with colC:
    c1, c2, c3 = st.columns([1,2,1])

    with c1:
        if st.button("◀"):
            if st.session_state.page > 1:
                st.session_state.page -= 1
                st.rerun()

    with c2:
        st.markdown(
            f"<div style='text-align:center;'>Page {st.session_state.page}/{total_pages}</div>",
            unsafe_allow_html=True
        )

    with c3:
        if st.button("▶"):
            if st.session_state.page < total_pages:
                st.session_state.page += 1
                st.rerun()

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
