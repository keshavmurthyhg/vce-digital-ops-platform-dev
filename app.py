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

/* ================= GLOBAL ================= */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
}

html, body, [class*="css"] {
    font-size: 13px !important;
}

/* ================= TABLE ================= */
table {
    border-collapse: collapse;
    width: 100%;
}

th {
    text-align: center !important;
    background-color: #f5f5f5;
    font-weight: 600;
    padding: 6px !important;
}

td {
    text-align: left;
    padding: 6px !important;
    white-space: nowrap;
}

tr:hover {
    background-color: #f9f9f9;
}

td:nth-child(3), th:nth-child(3) {
    max-width: 420px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

td:not(:nth-child(3)), th:not(:nth-child(3)) {
    width: 1%;
}

a {
    text-decoration: none;
    color: #1f77b4;
    font-weight: 500;
}

/* ================= STICKY SIDEBAR ================= */
section[data-testid="stSidebar"] {
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
}

/* ================= CLEAN SPACING ================= */
section[data-testid="stSidebar"] .stMarkdown {
    margin-bottom: 4px !important;
}

section[data-testid="stSidebar"] label {
    font-size: 13px !important;
    margin-bottom: 2px !important;
}

section[data-testid="stSidebar"] .stCheckbox {
    margin-bottom: 2px !important;
}

section[data-testid="stSidebar"] .stSelectbox {
    margin-bottom: 4px !important;
}

section[data-testid="stSidebar"] hr {
    margin: 6px 0 !important;
}

/* ================= SEARCH ================= */
input {
    padding: 6px !important;
}

button {
    padding: 4px 10px !important;
    font-size: 13px !important;
}

/* ===== FIX FILTER GAP (TARGETED) ===== */

/* Reduce expander content padding */
section[data-testid="stSidebar"] div[role="region"] {
    padding-top: 4px !important;
    padding-bottom: 4px !important;
}

/* Reduce spacing between elements inside expander */
section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] > div {
    margin-bottom: 2px !important;
    padding-bottom: 0px !important;
}

/* Tighten markdown labels like Status / Priority */
section[data-testid="stSidebar"] .stMarkdown p {
    margin-bottom: 2px !important;
}

/* Reduce selectbox spacing */
section[data-testid="stSidebar"] .stSelectbox {
    margin-bottom: 2px !important;
}

/* Reduce internal selectbox padding */
section[data-testid="stSidebar"] div[data-baseweb="select"] {
    margin-top: 0px !important;
    margin-bottom: 2px !important;
}

/* Reduce gap between label and dropdown */
section[data-testid="stSidebar"] label {
    margin-bottom: 0px !important;
}

/* ===== ULTRA COMPACT SIDEBAR ===== */

/* Remove almost all vertical spacing */
section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] > div {
    margin-bottom: 1px !important;
    padding-bottom: 0px !important;
}

/* Inline label + dropdown */
.inline-filter {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 2px;
}

/* Label styling */
.inline-filter label {
    min-width: 55px;
    font-size: 12px !important;
    font-weight: 500;
    margin: 0 !important;
}

/* Dropdown tight */
section[data-testid="stSidebar"] div[data-baseweb="select"] {
    margin: 0 !important;
}

/* Expander tighter */
section[data-testid="stSidebar"] div[role="region"] {
    padding-top: 2px !important;
    padding-bottom: 2px !important;
}

/* Checkbox tighter */
section[data-testid="stSidebar"] .stCheckbox {
    margin-bottom: 1px !important;
}

</style>
""", unsafe_allow_html=True)

# ================= TITLE =================
st.title("Ops Insight Dashboard")

# ================= LOAD =================
df, last_refresh = load_data()

# ================= DEFAULT FILTER VALUES =================
status = []
priority = []

# ================= SIDEBAR =================
st.sidebar.markdown("## 📊 Menu")
st.sidebar.selectbox("", ["Search Tool"])

# ================= SOURCE =================
#with st.sidebar.expander("📂 Source", expanded=True):

 #   c1, c2 = st.columns(2)

   # with c1:
   #     all_src = st.checkbox("ALL", value=True)

   # with c2:
    #    azure = st.checkbox("AZURE", value=all_src)
    #    snow = st.checkbox("SNOW", value=all_src)
     #   ptc = st.checkbox("PTC", value=all_src)

   # if all_src:
    #    sources = ["AZURE", "SNOW", "PTC"]
  #  else:
    #    sources = []
    #    if azure: sources.append("AZURE")
    #    if snow: sources.append("SNOW")
    #    if ptc: sources.append("PTC")

with st.sidebar.expander("📂 Source", expanded=True):

    cols = st.columns(2)

    all_src = cols[0].checkbox("ALL", value=True)
    azure = cols[1].checkbox("AZURE", value=all_src)

    snow = cols[0].checkbox("SNOW", value=all_src)
    ptc = cols[1].checkbox("PTC", value=all_src)

    if all_src:
        sources = ["AZURE", "SNOW", "PTC"]
    else:
        sources = []
        if azure: sources.append("AZURE")
        if snow: sources.append("SNOW")
        if ptc: sources.append("PTC")

    if not sources:
        st.stop()
# ================= FILTER =================
filtered = df[df["Source"].isin(sources)].copy()

#with st.sidebar.expander("🎯 Filters", expanded=True):

   # st.markdown("**Status**")
  #  status_list = ["ALL"] + sorted(filtered["Status"].dropna().unique())
  #  status = st.selectbox("", status_list)

 #   st.markdown("**Priority**")

 #   def clean_priority(x):
  #      m = re.search(r"(Severity\s*[1-4]|Priority\s*[1-4])", str(x))
   #     return m.group(0) if m else str(x)

  #  filtered["Priority"] = filtered["Priority"].apply(clean_priority)
#
   # priority_list = ["ALL"] + sorted(filtered["Priority"].dropna().unique())
  #  priority = st.selectbox("", priority_list)

#========== Inline filters ======================

#with st.sidebar.expander("🎯 Filters", expanded=True):

 #   # STATUS (INLINE)
  #  col1, col2 = st.columns([1,3])
   # with col1:
   #     st.markdown("**Status**")
  #  with col2:
   #     status_list = ["ALL"] + sorted(filtered["Status"].dropna().unique())
   #     status = st.selectbox("", status_list, key="status")

    # PRIORITY (INLINE)
#    col1, col2 = st.columns([1,3])
 #   with col1:
  #      st.markdown("**Priority**")
  #  with col2:
     #   def clean_priority(x):
     #      m = re.search(r"(Severity\s*[1-4]|Priority\s*[1-4])", str(x))
      #      return m.group(0) if m else str(x)

    #    filtered["Priority"] = filtered["Priority"].apply(clean_priority)

     #   priority_list = ["ALL"] + sorted(filtered["Priority"].dropna().unique())
     #   priority = st.selectbox("", priority_list, key="priority")

# ================ APPLY FILTER ==========================
#if status != "ALL":
 #   filtered = filtered[filtered["Status"] == status]

#if priority != "ALL":
  #  filtered = filtered[filtered["Priority"] == priority]

# ---------- APPLY FILTERS ----------

#if status:
  #  filtered = filtered[filtered["Status"].isin(status)]

#if priority:
 #   filtered = filtered[filtered["Priority"].isin(priority)]

# ---------- APPLY FILTERS ----------

#if len(status) > 0:
  #  filtered = filtered[filtered["Status"].isin(status)]

#if len(priority) > 0:
 #   filtered = filtered[filtered["Priority"].isin(priority)]

# ================= APPLY FILTER =================

if status is not None and len(status) > 0:
    filtered = filtered[filtered["Status"].isin(status)]

if priority is not None and len(priority) > 0:
    filtered = filtered[filtered["Priority"].isin(priority)]



#================= Multi-selection filters ==========================
#with st.sidebar.expander("🎯 Filters", expanded=True):

    # ---------- STATUS (MULTI SELECT) ----------
   # status_options = sorted(filtered["Status"].dropna().unique())
  #  status = st.multiselect(
   #     "Status",
    #    options=status_options,
    #    default=[],
   #     placeholder="All"
  #  )

    # ---------- PRIORITY (MULTI SELECT) ----------
  #  def clean_priority(x):
   #     m = re.search(r"(Severity\s*[1-4]|Priority\s*[1-4])", str(x))
   #     return m.group(0) if m else str(x)

   # filtered["Priority"] = filtered["Priority"].apply(clean_priority)

   # priority_options = sorted(filtered["Priority"].dropna().unique())
   # priority = st.multiselect(
    #    "Priority",
    #    options=priority_options,
    #    default=[],
    #    placeholder="All"
  #  )

#with st.sidebar.expander("🎯 Filters", expanded=True):

    # ---------- STATUS ----------
  #  status_options = sorted(filtered["Status"].dropna().unique())

  #  status = st.multiselect(
  #      "Status",
  #      options=status_options,
  #      default=[]
  #  )

    # ---------- PRIORITY ----------
  #  def clean_priority(x):
   #     m = re.search(r"(Severity\s*[1-4]|Priority\s*[1-4])", str(x))
  #      return m.group(0) if m else str(x)

#    filtered["Priority"] = filtered["Priority"].apply(clean_priority)

  #  priority_options = sorted(filtered["Priority"].dropna().unique())

  #  priority = st.multiselect(
  #      "Priority",
  #      options=priority_options,
 #       default=[]
#    )

filtered = df[df["Source"].isin(sources)].copy()

with st.sidebar.expander("🎯 Filters", expanded=True):

    status_options = sorted(filtered["Status"].dropna().unique())

    status = st.multiselect(
        "Status",
        options=status_options,
        default=[]
    )

    priority_options = sorted(filtered["Priority"].dropna().unique())

    priority = st.multiselect(
        "Priority",
        options=priority_options,
        default=[]
    )

status = st.session_state.get("status", [])
priority = st.session_state.get("priority", [])

# ================= SEARCH =================
def clear_search():
    st.session_state["search_box"] = ""
    st.session_state["page"] = 1

if "search_box" not in st.session_state:
    st.session_state["search_box"] = ""

col1, col2 = st.columns([10,1])

with col1:
    st.text_input("🔎 Search", key="search_box")

with col2:
    st.button("❌", on_click=clear_search)

filtered = apply_search(filtered, st.session_state["search_box"])

# ================= COLOR STATUS IN TABLE =================

def color_status(val):
    val = str(val).lower()

    if "open" in val or "active" in val:
        return "color:red; font-weight:600;"
    elif "closed" in val:
        return "color:green; font-weight:600;"
    elif "cancel" in val:
        return "color:gray; font-weight:600;"
    else:
        return ""


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

# ================= HEADER =================
colA, colB, colC = st.columns([4,3,3])

with colA:
    st.markdown(f"<div style='font-size:16px; font-weight:600;'>Results: {total_rows}</div>", unsafe_allow_html=True)
    vc = filtered["Source"].value_counts()
    st.caption(f"AZURE: {vc.get('AZURE',0)} | SNOW: {vc.get('SNOW',0)} | PTC: {vc.get('PTC',0)}")

with colB:
    def to_excel(df):
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        return buffer.getvalue()

    st.download_button("📥 Download Excel", to_excel(filtered), "ops_data.xlsx")

with colC:
    c1, c2, c3 = st.columns([1,2,1])

    with c1:
        if st.button("◀") and st.session_state.page > 1:
            st.session_state.page -= 1
            st.rerun()

    with c2:
        st.markdown(f"<div style='text-align:center;'>Page {st.session_state.page}/{total_pages}</div>", unsafe_allow_html=True)

    with c3:
        if st.button("▶") and st.session_state.page < total_pages:
            st.session_state.page += 1
            st.rerun()

# ================= TABLE =================
#st.write(page_df.to_html(escape=False, index=False), unsafe_allow_html=True)

# =========== COLOR STATUS IN TABLE =============

#styled_df = page_df.style.applymap(
#    color_status,
#    subset=["Status"]
#)

#st.write(styled_df.to_html(escape=False), unsafe_allow_html=True)

# ================= TABLE =================

if not page_df.empty and "Status" in page_df.columns:

    def color_status(val):
        val = str(val).lower()

        if "open" in val or "active" in val:
            return "color:red; font-weight:600;"
        elif "closed" in val:
            return "color:green; font-weight:600;"
        elif "cancel" in val:
            return "color:gray; font-weight:600;"
        else:
            return ""

    styled_df = page_df.style.map(color_status, subset=["Status"])

    st.write(styled_df.to_html(escape=False), unsafe_allow_html=True)

else:
    st.warning("No data available")


# ================= KPI =================
with st.sidebar.expander("📈 KPI", expanded=True):

    kpi = calculate_kpi(filtered)

    c1,c2 = st.columns(2)
    c1.metric("Total", kpi["total"])
    c2.metric("Open", kpi["open"])

    c3,c4 = st.columns(2)
    c3.metric("Closed", kpi["closed"])
    c4.metric("Cancelled", kpi["cancelled"])

# ================= REFRESH =================
st.caption(f"Last refreshed: {last_refresh}")
