import streamlit as st
import pandas as pd
import io

from modules.data_loader import load_data
from modules.search import apply_search
from modules.kpi import calculate_kpi
from modules.table import render_table


def render_search_page():

    st.title("Ops Insight Dashboard")

    df, last_refresh = load_data()

    # ---------- SIDEBAR ----------
    st.sidebar.markdown("### 📂 Source")

    sources = []
    if st.sidebar.checkbox("AZURE", True):
        sources.append("AZURE")
    if st.sidebar.checkbox("SNOW", True):
        sources.append("SNOW")
    if st.sidebar.checkbox("PTC", True):
        sources.append("PTC")

    if not sources:
        st.warning("Select at least one source")
        return

    filtered = df[df["Source"].isin(sources)].copy()

    # ---------- SEARCH ----------
    col1, col2, col3, col4, col5 = st.columns([5,1,2,1,1])

    with col1:
        search_value = st.text_input("🔎 Search")

    with col2:
        if st.button("❌"):
            st.rerun()

    filtered = apply_search(filtered, search_value)

    # ---------- COUNT ----------
    total = len(filtered)
    vc = filtered["Source"].value_counts()

    with col3:
        st.markdown(f"**{total} Results**")
        st.caption(
            f"AZURE: {vc.get('AZURE',0)} | "
            f"SNOW: {vc.get('SNOW',0)} | "
            f"PTC: {vc.get('PTC',0)}"
        )

    # ---------- PAGINATION ----------
    with col4:
        rows = st.selectbox("Rows", [10,20,50], index=0)

    total_pages = max(1, (total // rows) + (1 if total % rows else 0))

    with col5:
        page = st.selectbox("Page", list(range(1, total_pages+1)))

    start = (page - 1) * rows
    end = start + rows

    df_display = filtered.reset_index(drop=True)
    df_display.insert(0, "SL No", range(1, len(df_display)+1))

    page_df = df_display.iloc[start:end]

    # ---------- DATE FORMAT ----------
    for col in ["Created Date", "Resolved Date"]:
        if col in page_df:
            page_df[col] = pd.to_datetime(page_df[col], errors="coerce").dt.strftime("%d-%b-%y")

    page_df = page_df.fillna("")

    # ---------- TABLE ----------
    render_table(page_df)

    # ---------- DOWNLOAD ----------
    def to_excel(df):
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        return buffer.getvalue()

    st.download_button("📥 Download", to_excel(filtered), "ops_data.xlsx")

    # ---------- KPI ----------
    kpi = calculate_kpi(filtered)

    st.sidebar.markdown("### 📊 KPI")
    st.sidebar.write(f"Total: {kpi['total']}")
    st.sidebar.write(f"Open: {kpi['open']}")
    st.sidebar.write(f"Closed: {kpi['closed']}")
    st.sidebar.write(f"Cancelled: {kpi['cancelled']}")

    st.caption(f"Last refreshed: {last_refresh}")
