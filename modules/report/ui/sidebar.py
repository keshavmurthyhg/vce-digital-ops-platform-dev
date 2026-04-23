import streamlit as st

def render_sidebar(df):

    st.sidebar.header("Filters")

    priorities = st.sidebar.multiselect(
        "Priority",
        options=sorted(df["priority"].dropna().unique())
    )

    date_range = st.sidebar.date_input("Created Date Range")

    # Apply filters
    filtered = df.copy()

    if priorities:
        filtered = filtered[filtered["priority"].isin(priorities)]

    if len(date_range) == 2:
        start, end = date_range
        filtered["created"] = filtered["created"].astype("datetime64[ns]")
        filtered = filtered[
            (filtered["created"] >= str(start)) &
            (filtered["created"] <= str(end))
        ]

    return filtered
