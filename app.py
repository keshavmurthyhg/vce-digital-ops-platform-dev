import streamlit as st
import pandas as pd

from modules.data_loader import load_data
from modules.filters import apply_filters
from modules.search import apply_search
from modules.kpi import calculate_kpi

st.set_page_config(layout="wide")

# ---------- LOAD ----------
df, last_refresh = load_data()

# ---------- SESSION ----------
if "page" not in st.session_state:
    st.session_state.page = 1

# ---------- SIDEBAR ----------
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

status = st.sidebar.selectbox("Status", ["ALL"] + sorted(df["Status"].dropna().unique()))
priority = st.sidebar.selectbox("Priority", ["ALL"] + sorted(df["Priority"].dropna().unique()))

st.sidebar.markdown("---")

# ---------- SEARCH ----------
col1, col2 = st.columns([4,1])

with col1:
    keyword = st.text_input("🔎 Search", key="search")

with col2:
    if st.button("❌"):
        st.session_state.search = ""
        st.rerun()

# ---------- FILTER ----------
filtered = df[df["Source"].isin(sources)]
filtered = apply_filters(filtered, status, priority)
filtered = apply_search(filtered, keyword)

# ---------- RESET PAGE ----------
current = str(sources)+status+priority+str(keyword)
if "prev" not in st.session_state:
    st.session_state.prev = ""

if current != st.session_state.prev:
    st.session_state.page = 1
    st.session_state.prev = current

# ---------- PAGINATION ----------
total = len(filtered)
page_size = st.selectbox("", [5,10,20], index=1)
total_pages = max((total + page_size - 1)//page_size,1)

col1, col2, col3, col4 = st.columns([5,1,2,2])

with col1:
    st.markdown(f"### Results: {total}")
    c = filtered["Source"].value_counts()
    st.caption(f"AZURE: {c.get('AZURE',0)} | SNOW: {c.get('SNOW',0)} | PTC: {c.get('PTC',0)}")

with col2:
    prev_btn = st.button("◀")

with col3:
    st.markdown(f"<div style='text-align:center;'>Page {st.session_state.page}/{total_pages}</div>", unsafe_allow_html=True)

with col4:
    next_btn = st.button("▶")

if prev_btn and st.session_state.page > 1:
    st.session_state.page -= 1

if next_btn and st.session_state.page < total_pages:
    st.session_state.page += 1

start = (st.session_state.page-1)*page_size
end = start+page_size
page_df = filtered.iloc[start:end].copy()

# ---------- CLEAN ----------
page_df.reset_index(drop=True, inplace=True)
page_df.insert(0,"SL No", range(start+1,start+len(page_df)+1))

def clean(x):
    return str(x).split("<")[0].strip() if pd.notna(x) else x

for col in ["Created By","Assigned To"]:
    if col in page_df:
        page_df[col] = page_df[col].apply(clean)

for col in ["Created Date","Resolved Date"]:
    if col in page_df:
        page_df[col] = pd.to_datetime(page_df[col], errors="coerce").dt.strftime("%d-%b-%y")

def link(x):
    if pd.isna(x): return ""
    url = f"https://support.ptc.com/appserver/cs/view/case.jsp?n={x}"
    return f'<a href="{url}" target="_blank">Open</a>'

page_df["Link"] = page_df["Number"].apply(link)

# ---------- DISPLAY ----------
st.write(page_df.to_html(escape=False, index=False), unsafe_allow_html=True)

# ---------- KPI ----------
st.sidebar.markdown("### KPI")

kpi = calculate_kpi(filtered)

c1,c2 = st.sidebar.columns(2)
c1.metric("Total", kpi["total"])
c2.metric("Open", kpi["open"])

c3,c4 = st.sidebar.columns(2)
c3.metric("Closed", kpi["closed"])
c4.metric("Cancelled", kpi["cancelled"])

st.caption(f"Last refreshed: {last_refresh}")
