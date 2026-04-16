import streamlit as st
import pandas as pd
import re
import io

from modules.data_loader import load_data
from modules.search import apply_search
from modules.kpi import calculate_kpi


def render_search_page():

    st.title("Ops Insight Dashboard")

    df, last_refresh = load_data()

    def clean_priority(row):
        if row["Source"] == "PTC":
            m = re.search(r"Severity\s*([1-3])", str(row["Priority"]))
            return f"Severity {m.group(1)}" if m else ""
        return row["Priority"]

    df["Priority"] = df.apply(clean_priority, axis=1)

    # ================= SOURCE =================
    with st.sidebar.expander("📂 Source", True):
        cols = st.columns(2)

        all_src = cols[0].checkbox("ALL", True)
        azure = cols[1].checkbox("AZURE", all_src)
        snow = cols[0].checkbox("SNOW", all_src)
        ptc = cols[1].checkbox("PTC", all_src)

        sources = ["AZURE","SNOW","PTC"] if all_src else []
        if not all_src:
            if azure: sources.append("AZURE")
            if snow: sources.append("SNOW")
            if ptc: sources.append("PTC")

        if not sources:
            st.stop()

    filtered = df[df["Source"].isin(sources)].copy()

    # ================= FILTER =================
    with st.sidebar.expander("🎯 Filters", True):
        status = st.multiselect("Status", sorted(filtered["Status"].dropna().unique()))
        priority = st.multiselect("Priority", sorted(filtered["Priority"].dropna().unique()))

    if status:
        filtered = filtered[filtered["Status"].isin(status)]
    if priority:
        filtered = filtered[filtered["Priority"].isin(priority)]

    # ================= TOOLBAR =================
    col1, col2, col3, col4, col5, col6 = st.columns([5,1,2,1.5,1.5,2])

    search_value = col1.text_input("🔎 Search", key="search_box")

    col2.markdown("<div style='margin-top:30px'></div>", unsafe_allow_html=True)
    col2.button("❌", on_click=clear_all)
    
    def clear_all():
        st.session_state["search_box"] = ""
        st.session_state["page"] = 1
        st.session_state["rows"] = 10
        filtered = apply_search(filtered, search_value)

    df_display = filtered.reset_index(drop=True)
    df_display.insert(0, "SL No", range(1, len(df_display)+1))

    total_rows = len(df_display)

    # ✅ RESULT + SOURCE COUNT
    vc = filtered["Source"].value_counts()

    col3.markdown(f"<b>{total_rows}</b> Results", unsafe_allow_html=True)
    col3.markdown(
        f"<div style='font-size:12px;'>"
        f"AZURE: {vc.get('AZURE',0)} | "
        f"SNOW: {vc.get('SNOW',0)} | "
        f"PTC: {vc.get('PTC',0)}"
        f"</div>",
        unsafe_allow_html=True
    )

    page_size = col4.selectbox("Rows", [10,20,50,100])
    total_pages = max(1, (total_rows // page_size) + (1 if total_rows % page_size else 0))
    page = col5.selectbox("Page", list(range(1, total_pages + 1)))

    def to_excel(df):
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        return buffer.getvalue()

    with col6:
    st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)

    st.download_button(
        "📥 Download",
        to_excel(filtered),
        "ops_data.xlsx"
    )

    start = (page - 1) * page_size
    end = start + page_size
    page_df = df_display.iloc[start:end]

    # DATE FORMAT
    for col in ["Created Date","Resolved Date"]:
        if col in page_df:
            page_df[col] = pd.to_datetime(page_df[col], errors="coerce").dt.strftime("%d-%b-%y")

    page_df = page_df.fillna("")

    def make_link(row):
        num = str(row["Number"])
        return f'<a href="#" target="_blank">Open</a>'

    page_df["Open"] = page_df.apply(make_link, axis=1)

    st.write(page_df.to_html(escape=False, index=False), unsafe_allow_html=True)

    # KPI
    with st.sidebar.expander("📈 KPI", True):
        kpi = calculate_kpi(filtered)

        c1,c2 = st.columns(2)
        c1.metric("Total", kpi["total"])
        c2.metric("Open", kpi["open"])

        c3,c4 = st.columns(2)
        c3.metric("Closed", kpi["closed"])
        c4.metric("Cancelled", kpi["cancelled"])

    st.caption(f"Last refreshed: {last_refresh}")
