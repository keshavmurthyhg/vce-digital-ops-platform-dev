import streamlit as st
import pandas as pd
import re
import io

from modules.search.data_loader import load_data
from modules.search.search_logic import apply_all_filters
from modules.search.kpi import calculate_kpi


def render():
    st.title("Ops Insight Dashboard")

    df, last_refresh = load_data()

    # ---------- PRIORITY CLEAN ----------
    def clean_priority(row):
        if row["Source"] == "PTC":
            m = re.search(r"Severity\s*([1-3])", str(row["Priority"]))
            return f"Severity {m.group(1)}" if m else ""
        return row["Priority"]

    df["Priority"] = df.apply(clean_priority, axis=1)

    # ---------- SIDEBAR ----------
    sources = st.sidebar.multiselect(
        "Source",
        ["AZURE", "SNOW", "PTC"],
        default=["AZURE", "SNOW", "PTC"]
    )

    if not sources:
        st.warning("Select at least one source")
        return

    filtered = df[df["Source"].isin(sources)].copy()

    status = st.sidebar.multiselect(
        "Status",
        sorted(filtered["Status"].dropna().unique())
    )

    priority = st.sidebar.multiselect(
        "Priority",
        sorted(filtered["Priority"].dropna().unique())
    )

    search_value = st.text_input("🔎 Search")

    # ---------- APPLY LOGIC ----------
    filtered = apply_all_filters(filtered, status, priority, search_value)

    # ---------- KPI ----------
    kpi = calculate_kpi(filtered)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", kpi["total"])
    c2.metric("Open", kpi["open"])
    c3.metric("Closed", kpi["closed"])
    c4.metric("Cancelled", kpi["cancelled"])

    # ---------- DOWNLOAD ----------
    def to_excel(df):
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        return buffer.getvalue()

    st.download_button("📥 Download", to_excel(filtered), "ops_data.xlsx")

    # ---------- TABLE ----------
    st.dataframe(filtered, use_container_width=True)

    st.caption(f"Last refreshed: {last_refresh}")
