import streamlit as st
import pandas as pd

def render():
    st.title("📊 Analytics")

    # existing charts code here

    from modules.search.data_loader import load_data
    from modules.search.search import apply_search
    from modules.search.kpi import calculate_kpi
    
    
    def render_charts_page():
    
        st.title("📊 Ops Insights - Trends & Metrics")
    
        df, last_refresh = load_data()
    
        # ---------- SIDEBAR (REUSED) ----------
        with st.sidebar.expander("📂 Source", True):
            cols = st.columns(2)
    
            all_src = cols[0].checkbox("ALL", True)
            azure = cols[1].checkbox("AZURE", all_src)
            snow = cols[0].checkbox("SNOW", all_src)
            ptc = cols[1].checkbox("PTC", all_src)
    
            sources = ["AZURE", "SNOW", "PTC"] if all_src else []
            if not all_src:
                if azure: sources.append("AZURE")
                if snow: sources.append("SNOW")
                if ptc: sources.append("PTC")
    
            if not sources:
                st.stop()
    
        filtered = df[df["Source"].isin(sources)].copy()
    
        # ---------- SEARCH ----------
        search_value = st.sidebar.text_input("🔎 Search")
        filtered = apply_search(filtered, search_value)
    
        # ---------- KPI ----------
        kpi = calculate_kpi(filtered)
    
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total", kpi["total"])
        c2.metric("Open", kpi["open"])
        c3.metric("Closed", kpi["closed"])
        c4.metric("Cancelled", kpi["cancelled"])
    
        # ---------- DATE PREP ----------
        filtered["Created Date"] = pd.to_datetime(filtered["Created Date"], errors="coerce")
    
        # ---------- TREND: DAILY ----------
        st.subheader("📈 Tickets Trend (Daily)")
    
        daily = (
            filtered
            .groupby(filtered["Created Date"].dt.date)
            .size()
            .reset_index(name="Count")
        )
    
        daily = daily.sort_values("Created Date")
    
        st.line_chart(daily.set_index("Created Date"))
    
        # ---------- TREND: SOURCE ----------
        st.subheader("📊 Tickets by Source")
    
        src = filtered["Source"].value_counts()
        st.bar_chart(src)
    
        # ---------- TREND: STATUS ----------
        st.subheader("📊 Tickets by Status")
    
        status = filtered["Status"].value_counts()
        st.bar_chart(status)
    
        # ---------- TREND: PRIORITY ----------
        st.subheader("📊 Tickets by Priority")
    
        priority = filtered["Priority"].value_counts()
        st.bar_chart(priority)
    
        # ---------- HEATMAP (MONTH vs SOURCE) ----------
        st.subheader("🔥 Monthly Trend by Source")
    
        filtered["Month"] = filtered["Created Date"].dt.to_period("M").astype(str)
    
        heatmap = (
            filtered
            .groupby(["Month", "Source"])
            .size()
            .unstack(fill_value=0)
        )
    
        st.dataframe(heatmap)
    
        st.caption(f"Last refreshed: {last_refresh}")
