import streamlit as st
import pandas as pd

from modules.search.data_loader import load_data
from modules.search.search import apply_search
from modules.search.kpi import calculate_kpi


def render():

    st.title("📊 Ops Insights - Trends & Metrics")

    # ---------- LOAD ----------
    df, last_refresh = load_data()

    if df.empty:
        st.warning("No data available")
        return

    # ---------- FILTER (NO SIDEBAR) ----------
    st.subheader("Filters")

    col1, col2 = st.columns(2)

    with col1:
        sources = st.multiselect(
            "Source",
            ["AZURE", "SNOW", "PTC"],
            default=["AZURE", "SNOW", "PTC"]
        )

    with col2:
        search_value = st.text_input("🔎 Search")

    if not sources:
        st.warning("Select at least one source")
        return

    filtered = df[df["Source"].isin(sources)].copy()
    filtered = apply_search(filtered, search_value)

    # ---------- KPI ----------
    kpi = calculate_kpi(filtered)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", kpi["total"])
    c2.metric("Open", kpi["open"])
    c3.metric("Closed", kpi["closed"])
    c4.metric("Cancelled", kpi["cancelled"])

    # ---------- DATE ----------
    filtered["Created Date"] = pd.to_datetime(
        filtered["Created Date"], errors="coerce"
    )

    # ---------- DAILY TREND ----------
    st.subheader("📈 Tickets Trend (Daily)")

    daily = (
        filtered
        .groupby(filtered["Created Date"].dt.date)
        .size()
        .reset_index(name="Count")
        .sort_values("Created Date")
    )

    st.line_chart(daily.set_index("Created Date"))

    # ---------- SOURCE ----------
    st.subheader("📊 Tickets by Source")
    st.bar_chart(filtered["Source"].value_counts())

    # ---------- STATUS ----------
    st.subheader("📊 Tickets by Status")
    st.bar_chart(filtered["Status"].value_counts())

    # ---------- PRIORITY ----------
    st.subheader("📊 Tickets by Priority")
    st.bar_chart(filtered["Priority"].value_counts())

    # ---------- HEATMAP ----------
    st.subheader("🔥 Monthly Trend by Source")

    filtered["Month"] = filtered["Created Date"].dt.to_period("M").astype(str)

    heatmap = (
        filtered
        .groupby(["Month", "Source"])
        .size()
        .unstack(fill_value=0)
    )

    st.dataframe(heatmap, use_container_width=True)

    st.caption(f"Last refreshed: {last_refresh}")
