import streamlit as st
import pandas as pd
import re
import io

from modules.search.data_loader import load_data
from modules.search.search import apply_search
from modules.search.kpi import calculate_kpi
from modules.search.user_group import load_or_create_mapping, save_mapping


def render():

    st.set_page_config(layout="wide")
    st.title("Ops Insight Dashboard")

    df, last_refresh = load_data()

    # ---------- USER GROUP ----------
    mapping_df = load_or_create_mapping(df)

    group_map = dict(zip(mapping_df["Name"], mapping_df["Group"]))

    df["Assigned Group"] = df["Assigned To"].map(group_map).fillna("Unassigned")
    df["Created Group"] = df["Created By"].map(group_map).fillna("Unassigned")

    # ---------- PRIORITY CLEAN ----------
    def clean_priority(row):
        if row["Source"] == "PTC":
            m = re.search(r"Severity\s*([1-3])", str(row["Priority"]))
            return f"Severity {m.group(1)}" if m else ""
        return row["Priority"]

    df["Priority"] = df.apply(clean_priority, axis=1)

    # ---------- SIDEBAR SOURCE ----------
    with st.sidebar.expander("📂 Source", True):
        cols = st.columns(2)

        all_src = cols[0].checkbox("ALL", True)
        azure = cols[1].checkbox("AZURE", all_src)
        snow = cols[0].checkbox("SNOW", all_src)
        ptc = cols[1].checkbox("PTC", all_src)

        sources = ["AZURE", "SNOW", "PTC"] if all_src else []
        if not all_src:
            if azure:
                sources.append("AZURE")
            if snow:
                sources.append("SNOW")
            if ptc:
                sources.append("PTC")

        if not sources:
            st.stop()

    filtered = df[df["Source"].isin(sources)].copy()

    # ---------- USER GROUP EDITOR ----------
    with st.sidebar.expander("👥 User Group Mapping", False):

        edited_mapping = st.data_editor(
            mapping_df,
            num_rows="dynamic",
            use_container_width=True
        )

        if st.button("💾 Save Groups"):
            save_mapping(edited_mapping)
            st.success("Mapping saved!")

    # ---------- FILTER ----------
    with st.sidebar.expander("🎯 Filters", True):

        status = st.multiselect(
            "Status",
            sorted(filtered["Status"].dropna().unique())
        )

        priority = st.multiselect(
            "Priority",
            sorted(filtered["Priority"].dropna().unique())
        )

        created_by = st.multiselect(
            "Created By",
            sorted(filtered["Created By"].dropna().unique())
        )

        assigned_to = st.multiselect(
            "Assigned To",
            sorted(filtered["Assigned To"].dropna().unique())
        )

        group = st.multiselect(
            "Group",
            sorted(filtered["Assigned Group"].dropna().unique())
        )

    # ---------- APPLY FILTER ----------
    if status:
        filtered = filtered[filtered["Status"].isin(status)]

    if priority:
        filtered = filtered[filtered["Priority"].isin(priority)]

    if created_by:
        filtered = filtered[filtered["Created By"].isin(created_by)]

    if assigned_to:
        filtered = filtered[filtered["Assigned To"].isin(assigned_to)]

    if group:
        filtered = filtered[filtered["Assigned Group"].isin(group)]

    # ---------- DATE FILTER ----------
    with st.sidebar.expander("📅 Date Filter", True):

        date_column = st.selectbox(
            "Select Date Field",
            ["Created Date", "Resolved Date"]
        )

        mode = st.radio(
            "Filter Type",
            ["No Filter", "Date Range", "By Year", "Quick Select"]
        )

        temp_dates = df[date_column]

        min_date = temp_dates.min()
        max_date = temp_dates.max()

        if mode == "Date Range":
            date_range = st.date_input(
                "Select Date Range",
                value=(min_date, max_date)
            )

        elif mode == "By Year":
            years = sorted(temp_dates.dt.year.dropna().unique())
            selected_year = st.selectbox("Select Year", years)

        elif mode == "Quick Select":
            quick_option = st.selectbox(
                "Quick Options",
                ["Last 7 Days", "Last 30 Days", "This Month"]
            )

    if mode != "No Filter":

        if mode == "Date Range" and len(date_range) == 2:
            start_date, end_date = date_range
            filtered = filtered[
                (filtered[date_column] >= pd.to_datetime(start_date)) &
                (filtered[date_column] <= pd.to_datetime(end_date))
            ]

        elif mode == "By Year":
            filtered = filtered[
                filtered[date_column].dt.year == selected_year
            ]

        elif mode == "Quick Select":
            today = pd.Timestamp.today()

            if quick_option == "Last 7 Days":
                start_date = today - pd.Timedelta(days=7)
            elif quick_option == "Last 30 Days":
                start_date = today - pd.Timedelta(days=30)
            else:
                start_date = today.replace(day=1)

            filtered = filtered[filtered[date_column] >= start_date]

    # ---------- SEARCH ----------
    search_value = st.text_input("🔎 Search", key="search_box")
    filtered = apply_search(filtered, search_value)

    # ---------- DISPLAY ----------
    df_display = filtered.reset_index(drop=True)
    df_display.insert(0, "SL No", range(1, len(df_display) + 1))

    st.write(df_display)

    # ---------- KPI ----------
    with st.sidebar.expander("📈 KPI", True):
        kpi = calculate_kpi(filtered)

        c1, c2 = st.columns(2)
        c1.metric("Total", kpi["total"])
        c2.metric("Open", kpi["open"])

        c3, c4 = st.columns(2)
        c3.metric("Closed", kpi["closed"])
        c4.metric("Cancelled", kpi["cancelled"])

    st.caption(f"Last refreshed: {last_refresh}")
