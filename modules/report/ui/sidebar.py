import streamlit as st
import pandas as pd
from datetime import date, timedelta

def render_sidebar(df):

    st.sidebar.header("Filters")

    priorities = st.sidebar.multiselect(
        "Priority",
        options=sorted(df["priority"].dropna().unique())
    )

    date_range = st.sidebar.date_input(
        "Created Date Range",
        value=(),
    )

    preset = st.sidebar.selectbox(
        "Quick Filter",
        ["None", "Last 7 Days", "Last 30 Days"]
    )

    from datetime import date, timedelta
    
    if preset == "Last 7 Days":
        date_range = (date.today() - timedelta(days=7), date.today())
    
    elif preset == "Last 30 Days":
        date_range = (date.today() - timedelta(days=30), date.today())
    
    # Apply filters
    filtered = df.copy()

    # Priority filter
    if priorities:
        filtered = filtered[filtered["priority"].isin(priorities)]

    # 🔹 Convert timestamp safely
    filtered["created"] = pd.to_datetime(filtered["created"], errors="coerce")

    # 🔹 Date filter (safe handling)
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = date_range
    
        filtered["created"] = pd.to_datetime(filtered["created"], errors="coerce")
    
        filtered = filtered[
            (filtered["created"].dt.date >= start) &
            (filtered["created"].dt.date <= end)
        ]

    #================= DOWNLOAD BUTTONS ================================
    st.sidebar.markdown("### Download")
    
    if "pdf_bytes" in st.session_state and "data" in st.session_state:
        st.sidebar.download_button(
            "⬇ Download PDF",
            data=st.session_state["pdf_bytes"],
            file_name=f"{st.session_state['data']['number']}.pdf",
            mime="application/pdf"
        )
    
    if "word_bytes" in st.session_state and "data" in st.session_state:
        st.sidebar.download_button(
            "⬇ Download Word",
            data=st.session_state["word_bytes"],
            file_name=f"{st.session_state['data']['number']}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    
    if "zip_bytes" in st.session_state and "data" in st.session_state:
        st.sidebar.download_button(
            "⬇ Download Word",
            data=st.session_state["zip_bytes"],
            file_name=f"Bulk_Report_{format_date('2026-01-01')}.zip",
            mime="application/zip"
        )
