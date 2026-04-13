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
.block-container { padding-top: 1rem !important; }

/* TABLE */
table { width:100%; border-collapse: collapse; }
th { text-align:center !important; padding:6px !important; background:#f5f5f5; font-size:13px;}
td { padding:6px !important; font-size:13px; white-space:nowrap !important; }

/* DESCRIPTION */
td:nth-child(3), th:nth-child(3) {
    max-width: 400px;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* PRIORITY */
td:nth-child(4), th:nth-child(4) { width:130px; }

/* DATE */
td:nth-child(7), th:nth-child(7),
td:nth-child(9), th:nth-child(9) { min-width:100px; }

/* KPI FONT */
[data-testid="stMetricValue"] { font-size:13px !important; }

/* STATUS COLORS */
.status-open {color:red;font-weight:600;}
.status-closed {color:green;font-weight:600;}
.status-cancel {color:gray;font-weight:600;}

/* ONLY PAGINATION DROPDOWN COMPACT */
div[data-testid="column"]:nth-child(2) div[data-baseweb="select"],
div[data-testid="column"]:nth-child(3) div[data-baseweb="select"] {
    min-width:70px !important;
    max-width:80px !important;
}

/* SIDEBAR FONT */
section[data-testid="stSidebar"] label {
    font-size:12px !important;
}

</style>
""", unsafe_allow_html=True)

# ================= TITLE =================
st.title("Ops Insight Dashboard")

# ================= LOAD =================
df, last_refresh = load_data()

# ================= PRIORITY FIX =================
def clean_priority(row):
    if row["Source"] == "PTC":
        m = re.search(r"Severity\s*([1-3])", str(row["Priority"]))
        return f"Severity {m.group(1)}" if m else ""
    return row["Priority"]

df["Priority"] = df.apply(clean_priority, axis=1)

# ================= SIDEBAR =================
st.sidebar.markdown("## 📊 Menu")
st.sidebar.selectbox("", ["Search Tool"])

with st.sidebar.expander("📂 Source", True):
    cols = st.columns(2)

    all_src = cols[0].checkbox("ALL", True)
    azure = cols[1].checkbox("AZURE", all_src)
    snow = cols[0].checkbox("SNOW", all_src)
    ptc = cols[1].checkbox("PTC", all_src)

    if all_src:
        sources = ["AZURE","SNOW","PTC"]
    else:
        sources = []
        if azure: sources.append("AZURE")
        if snow: sources.append("SNOW")
        if ptc: sources.append("PTC")

    if not sources:
        st.stop()

# ================= FILTER =================
filtered = df[df["Source"].isin(sources)].copy()

with st.sidebar.expander("🎯 Filters", True):
    status = st.multiselect("Status", sorted(filtered["Status"].dropna().unique()))
    priority = st.multiselect("Priority", sorted(filtered["Priority"].dropna().unique()))

if status:
    filtered = filtered[filtered["Status"].isin(status)]
if priority:
    filtered = filtered[filtered["Priority"].isin(priority)]

# ================= SEARCH =================
def clear_search():
    st.session_state.search_box = ""

if "search_box" not in st.session_state:
    st.session_state.search_box = ""

col1, col2 = st.columns([20,1])

with col1:
    search_value = st.text_input(
        "🔎 Search",
        value=st.session_state.search_box,
        key="search_box_input",
        label_visibility="collapsed"
    )

with col2:
    st.button("❌", on_click=clear_search)

filtered = apply_search(filtered, search_value)
st.session_state.search_box = search_value

# ================= DATA =================
df_display = filtered.copy().reset_index(drop=True)
df_display.insert(0, "SL No", range(1, len(df_display)+1))

def clean(x):
    return re.sub(r"\s*<.*?>|\(.*?\)", "", str(x)).strip()

for col in ["Created By","Assigned To"]:
    if col in df_display:
        df_display[col] = df_display[col].apply(clean)

for col in ["Created Date","Resolved Date"]:
    if col in df_display:
        df_display[col] = pd.to_datetime(df_display[col], errors="coerce").dt.strftime("%d-%b-%Y")

df_display["Description"] = df_display["Description"].apply(
    lambda x: x[:80] + "..." if len(str(x)) > 80 else x
)

df_display = df_display.fillna("")

# STATUS COLOR
def format_status(v):
    v = str(v).lower()
    if "open" in v or "active" in v:
        return f'<span class="status-open">{v}</span>'
    if "closed" in v:
        return f'<span class="status-closed">{v}</span>'
    if "cancel" in v:
        return f'<span class="status-cancel">{v}</span>'
    return v

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
total_rows = len(df_display)

colA, colB, colC, colD = st.columns([3,1,1,3])

with colA:
    st.markdown(f"**Results: {total_rows}**")
    vc = filtered["Source"].value_counts()
    st.caption(f"AZURE: {vc.get('AZURE',0)} | SNOW: {vc.get('SNOW',0)} | PTC: {vc.get('PTC',0)}")

with colB:
    page_size = st.selectbox("Rows", [10,20,50,100], key="page_size")

total_pages = max(1, (total_rows // page_size) + (1 if total_rows % page_size else 0))

with colC:
    page = st.selectbox("Page", list(range(1,total_pages+1)), key="page_number")

with colD:
    st.markdown("<div style='text-align:right'>", unsafe_allow_html=True)

    def to_excel(df):
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        return buffer.getvalue()

    st.download_button("📥 Download Excel", to_excel(filtered), "ops_data.xlsx")

    st.markdown("</div>", unsafe_allow_html=True)

# APPLY PAGINATION
start = (page-1)*page_size
end = start + page_size
page_df = df_display.iloc[start:end]

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
