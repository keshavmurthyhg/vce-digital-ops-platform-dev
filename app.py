import streamlit as st
import pandas as pd
import re
import io

from modules.snow_api import fetch_incident
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
.block-container { padding-top: 1rem !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# ================= WORD REPORT GENERATOR =====================
# ============================================================

if menu == "Word Report Generator":

    st.title("📄 SNOW Incident Report Generator")

    incident_number = st.text_input("Enter Incident Number", key="snow_input")

    col1, col2 = st.columns(2)

    if col1.button("Fetch Incident"):
        st.session_state.snow_data = fetch_incident(incident_number)

    if "snow_data" in st.session_state and st.session_state.snow_data:

        data = st.session_state.snow_data

        st.success("Incident ready")
        st.json(data)

        # Editable Inputs
        root_cause = st.text_area("Root Cause")
        l2_analysis = st.text_area("L2 Analysis")
        resolution = st.text_area("Resolution")
        closure = st.text_area("Closure Notes")

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

    # PRIORITY FIX
    def clean_priority(row):
        if row["Source"] == "PTC":
            m = re.search(r"Severity\s*([1-3])", str(row["Priority"]))
            return f"Severity {m.group(1)}" if m else ""
        return row["Priority"]

    df["Priority"] = df.apply(clean_priority, axis=1)

    # SIDEBAR FILTERS
    st.sidebar.markdown("## 📊 Filters")

    sources = st.sidebar.multiselect(
        "Source",
        ["AZURE", "SNOW", "PTC"],
        default=["AZURE", "SNOW", "PTC"]
    )

    filtered = df[df["Source"].isin(sources)]

    # SEARCH
    search_value = st.text_input("🔎 Search", key="search_box")
    filtered = apply_search(filtered, search_value)

    df_display = filtered.copy().reset_index(drop=True)
    df_display.insert(0, "SL No", range(1, len(df_display)+1))

    # CLEAN
    df_display = df_display.fillna("")

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

    # TABLE
    st.write(df_display.to_html(escape=False, index=False), unsafe_allow_html=True)

    # KPI
    kpi = calculate_kpi(filtered)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total", kpi["total"])
    c2.metric("Open", kpi["open"])
    c3.metric("Closed", kpi["closed"])

    st.caption(f"Last refreshed: {last_refresh}")
