import streamlit as st
import pandas as pd
import re
import io

from modules.doc_generator import generate_word_doc
from modules.data_loader import load_data
from modules.search import apply_search
from modules.kpi import calculate_kpi

st.set_page_config(layout="wide")

# ================= MENU =================
menu = st.sidebar.selectbox(
    "📊 Select Module",
    ["Search Dashboard", "Word Report Generator"]
)

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
    max-width: 300px;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* PRIORITY */
td:nth-child(4), th:nth-child(4) { width:130px; }

/* DATE */
td:nth-child(7), th:nth-child(7),
td:nth-child(9), th:nth-child(9) { min-width:110px; }

/* KPI */
[data-testid="stMetricValue"] { font-size:13px !important; }

/* STATUS */
.status-open {color:red;font-weight:600;}
.status-closed {color:green;font-weight:600;}
.status-cancel {color:gray;font-weight:600;}

/* TOOLBAR ALIGN */
div[data-testid="stHorizontalBlock"] {
    align-items: flex-end;
}

/* INPUT + BUTTON HEIGHT */
input { height:38px !important; }
button { height:38px !important; }

/* ONLY PAGINATION DROPDOWN COMPACT */
div[data-testid="column"]:nth-child(4) div[data-baseweb="select"],
div[data-testid="column"]:nth-child(5) div[data-baseweb="select"] {
    min-width:70px !important;
    max-width:85px !important;
}

/* SIDEBAR FONT */
section[data-testid="stSidebar"] label {
    font-size:12px !important;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# ================= WORD REPORT GENERATOR =====================
# ============================================================

def get_incident_from_df(df, incident_number):

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    row = df[df["number"].astype(str) == str(incident_number)]

    if not row.empty:
        row = row.iloc[0]

        return {
            "number": str(row.get("number", "")),
            "short_description": str(row.get("short description", "")),
            "description": str(row.get("description", "")),
            "priority": str(row.get("priority", "")),
            "state": str(row.get("status", "")),

            # ✅ EXACT COLUMN MATCH
            "work_notes": str(row.get("work notes", "")),
            "comments": str(row.get("additional comments", "")),
            "resolution": str(row.get("resolution notes", ""))
        }

    return None


if menu == "Word Report Generator":

    st.title("📄 SNOW Incident Report Generator")

    df, _ = load_data()

    incident_number = st.text_input("Enter Incident Number", key="snow_input")

    col1, col2 = st.columns(2)

    if "init_loaded" not in st.session_state:
        st.session_state.init_loaded = False

    if col1.button("Fetch Incident"):
        st.session_state.snow_data = get_incident_from_df(df, incident_number)
        st.session_state.init_loaded = False

    if "snow_data" in st.session_state and st.session_state.snow_data:

        data = st.session_state.snow_data

        if not st.session_state.init_loaded:
            st.session_state.root = data.get("work_notes", "")
            st.session_state.l2 = data.get("comments", "")
            st.session_state.res = data.get("resolution", "")
            st.session_state.closure = data.get("resolution", "")
            st.session_state.init_loaded = True

        root_cause = st.text_area("Root Cause", key="root")
        l2_analysis = st.text_area("L2 Analysis", key="l2")
        resolution = st.text_area("Resolution", key="res")
        closure = st.text_area("Closure Notes", key="closure")
    
        if col2.button("Generate Document"):

            file = generate_word_doc(
                data,
                root_cause,
                l2_analysis,
                resolution,
                closure
            )

            st.download_button(
                label="📥 Download Report",
                data=file,
                file_name=f"{incident_number}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

# ============================================================
# ================= SEARCH DASHBOARD ==========================
# ============================================================

if menu == "Search Dashboard":

    st.title("Ops Insight Dashboard")

    df, last_refresh = load_data()

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

    filtered = df[df["Source"].isin(sources)].copy()

    if "status_filter" not in st.session_state:
        st.session_state.status_filter = []
    if "priority_filter" not in st.session_state:
        st.session_state.priority_filter = []

    with st.sidebar.expander("🎯 Filters", True):
        status = st.multiselect(
            "Status",
            sorted(filtered["Status"].dropna().unique()),
            key="sidebar_status"
        )

        priority = st.multiselect(
            "Priority",
            sorted(filtered["Priority"].dropna().unique()),
            key="sidebar_priority"
        )

    if status:
        filtered = filtered[filtered["Status"].isin(status)]
    if priority:
        filtered = filtered[filtered["Priority"].isin(priority)]

    # ================= TOOLBAR =================
    def clear_all():
        st.session_state.toolbar_search = ""
        st.session_state.toolbar_page_number = 1
        st.session_state.toolbar_page_size = 10
        st.session_state.sidebar_status = []
        st.session_state.sidebar_priority = []

    if "toolbar_search" not in st.session_state:
        st.session_state.toolbar_search = ""

    col1, col2, col3, col4, col5, col6 = st.columns([5,1,2,1.5,1.5,2])

    with col1:
        search_value = st.text_input(
            "🔎 Search",
            value=st.session_state.toolbar_search,
            key="toolbar_search"
        )

    with col2:
        st.markdown("<div style='margin-top:30px'></div>", unsafe_allow_html=True)
        st.button("❌", on_click=clear_all)

    filtered = apply_search(filtered, search_value)

    df_display = filtered.copy().reset_index(drop=True)
    df_display.insert(0, "SL No", range(1, len(df_display)+1))

    total_rows = len(df_display)

    with col3:
        vc = filtered["Source"].value_counts()
        st.markdown(
            f"<div style='margin-top:8px;font-size:12px;'>"
            f"<b>{total_rows}</b> Results | "
            f"AZURE: {vc.get('AZURE',0)} | "
            f"SNOW: {vc.get('SNOW',0)} | "
            f"PTC: {vc.get('PTC',0)}"
            f"</div>",
            unsafe_allow_html=True
        )

    with col4:
        page_size = st.selectbox("Rows", [10,20,50,100], key="toolbar_page_size")

    total_pages = max(1, (total_rows // page_size) + (1 if total_rows % page_size else 0))

    with col5:
        page = st.selectbox("Page", list(range(1, total_pages + 1)), key="toolbar_page_number")

    with col6:
        def to_excel(df):
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            return buffer.getvalue()

        st.download_button("📥 Download", to_excel(filtered), "ops_data.xlsx")

    start = (page - 1) * page_size
    end = start + page_size
    page_df = df_display.iloc[start:end]

    # DATE FORMAT FIX
    for col in ["Created Date","Resolved Date"]:
        if col in page_df:
            page_df[col] = pd.to_datetime(page_df[col], errors="coerce").dt.strftime("%d-%b-%y")

    page_df = page_df.fillna("")

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

    page_df["Open"] = page_df.apply(make_link, axis=1)

    st.write(page_df.to_html(escape=False, index=False), unsafe_allow_html=True)

    with st.sidebar.expander("📈 KPI", True):
        kpi = calculate_kpi(filtered)

        c1,c2 = st.columns(2)
        c1.metric("Total", kpi["total"])
        c2.metric("Open", kpi["open"])

        c3,c4 = st.columns(2)
        c3.metric("Closed", kpi["closed"])
        c4.metric("Cancelled", kpi["cancelled"])

    st.caption(f"Last refreshed: {last_refresh}")
