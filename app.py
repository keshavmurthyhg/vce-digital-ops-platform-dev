import streamlit as st
import pandas as pd
import re

from modules.data_loader import load_data
from modules.filters import apply_filters
from modules.search import apply_search
from modules.kpi import calculate_kpi

st.set_page_config(layout="wide")

# ================= LOAD =================
df, last_refresh = load_data()

# ================= SESSION =================
if "page" not in st.session_state:
    st.session_state.page = 1

# ================= SIDEBAR =================
st.sidebar.title("Ops Insight Dashboard")

st.sidebar.markdown("### Source")
azure = st.sidebar.checkbox("AZURE")
snow = st.sidebar.checkbox("SNOW")
ptc = st.sidebar.checkbox("PTC")

sources = []
if azure: sources.append("AZURE")
if snow: sources.append("SNOW")
if ptc: sources.append("PTC")

if not sources:
    st.warning("⚠️ Please select at least one source")
    st.stop()

st.sidebar.markdown("---")

# ================= FILTERS =================
filtered = df[df["Source"].isin(sources)]

status_list = ["ALL"] + sorted(filtered["Status"].dropna().unique())
priority_list = ["ALL"] + sorted(filtered["Priority"].dropna().unique())

status = st.sidebar.selectbox("Status", status_list)
priority = st.sidebar.selectbox("Priority", priority_list)

filtered = apply_filters(filtered, status, priority)

st.sidebar.markdown("---")

# ================= SEARCH =================
col1, col2 = st.columns([4,1])

with col1:
    keyword = st.text_input("🔎 Search", key="search")

with col2:
    if st.button("❌"):
        st.session_state.search = ""
        st.rerun()

filtered = apply_search(filtered, keyword)

# ================= RESET PAGE =================
current = str(sources)+status+priority+str(keyword)

if "prev" not in st.session_state:
    st.session_state.prev = ""

if current != st.session_state.prev:
    st.session_state.page = 1
    st.session_state.prev = current

# ================= PAGINATION =================
total = len(filtered)
page_size = 10   # ✅ removed dropdown
total_pages = max((total + page_size - 1)//page_size,1)

col1, col2, col3 = st.columns([7,1,2])

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

st.caption(f"Page {st.session_state.page} / {total_pages}")

# ================= DATA SLICE =================
start = (st.session_state.page-1)*page_size
end = start+page_size

page_df = filtered.iloc[start:end].copy().reset_index(drop=True)

# ================= CLEAN =================
page_df.insert(0,"SL No", range(start+1,start+len(page_df)+1))
page_df = page_df.fillna("")

def clean_name(val):
    val = str(val)
    val = re.sub(r"\s*<.*?>", "", val)
    val = re.sub(r"\s*\(.*?\)", "", val)
    return val.strip()

for col in ["Created By","Assigned To"]:
    if col in page_df:
        page_df[col] = page_df[col].apply(clean_name)

for col in ["Created Date","Resolved Date"]:
    if col in page_df:
        page_df[col] = pd.to_datetime(page_df[col], errors="coerce").dt.strftime("%d-%b-%y")

# ================= LINK LOGIC =================
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

# ================= BADGE COLORS =================
def source_badge(val):
    if val == "AZURE":
        return "🔵 AZURE"
    elif val == "SNOW":
        return "🟢 SNOW"
    elif val == "PTC":
        return "🟠 PTC"
    return val

page_df["Source"] = page_df["Source"].apply(source_badge)

# ================= DISPLAY =================
event = st.dataframe(
    page_df,
    use_container_width=True,
    hide_index=True,
    selection_mode="single-row",
    on_select="rerun",
    column_config={
        "Description": st.column_config.TextColumn(width="large"),
        "URL": st.column_config.LinkColumn(
            "Open",
            help="Click row → opens ticket",
            display_text="Open"
        )
    }
)

# ================= CLICKABLE ROW =================
if event.selection.rows:
    selected_index = event.selection.rows[0]
    selected_row = page_df.iloc[selected_index]
    url = selected_row["URL"]

    if url:
        st.link_button("🔍 Open Selected Ticket", url)

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
