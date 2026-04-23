import streamlit as st
import pandas as pd

def render_sidebar(df):

    st.sidebar.header("Filters")

    priorities = st.sidebar.multiselect(
        "Priority",
        options=sorted(df["priority"].dropna().unique())
    )

    date_range = st.sidebar.date_input("Created Date Range")

    # Apply filters
    filtered = df.copy()

    # Priority filter
    if priorities:
        filtered = filtered[filtered["priority"].isin(priorities)]

    # 🔹 Convert timestamp safely
    filtered["created"] = pd.to_datetime(filtered["created"], errors="coerce")

    # 🔹 Date filter (safe handling)
    if isinstance(date_range, (list, tuple)):
        if len(date_range) == 2:
            start, end = date_range
        elif len(date_range) == 1:
            start = end = date_range[0]
        else:
            start = end = None

        if start and end:
            filtered = filtered[
                (filtered["created"] >= pd.to_datetime(start)) &
                (filtered["created"] <= pd.to_datetime(end))
            ]

    return filtered
