import streamlit as st
import pandas as pd
from datetime import date, timedelta

from modules.report.doc_generator import generate_pdf, generate_word_doc


def render_sidebar(df):

    st.sidebar.header("Filters")

    priorities = st.sidebar.multiselect(
        "Priority",
        options=sorted(df["priority"].dropna().unique())
    )

    # ✅ Clean date filter (no duplication)
    quick_filter = st.sidebar.selectbox(
        "Quick Filter",
        ["None", "Past Week", "Past Month", "Past 3 Months"]
    )

    if quick_filter == "Past Week":
        date_range = (date.today() - timedelta(days=7), date.today())
    elif quick_filter == "Past Month":
        date_range = (date.today() - timedelta(days=30), date.today())
    elif quick_filter == "Past 3 Months":
        date_range = (date.today() - timedelta(days=90), date.today())
    else:
        date_range = None

    # ---------------- FILTER ---------------- #
    filtered = df.copy()

    if priorities:
        filtered = filtered[filtered["priority"].isin(priorities)]

    filtered["created"] = pd.to_datetime(filtered["created"], errors="coerce")

    if date_range:
        start, end = date_range
        filtered = filtered[
            (filtered["created"].dt.date >= start) &
            (filtered["created"].dt.date <= end)
        ]

    # ---------------- ACTIONS ---------------- #

    st.sidebar.markdown("### Actions")

    st.sidebar.button("Apply to Bulk", use_container_width=True)

    if st.sidebar.button("Generate PDF", use_container_width=True):
        if "data" in st.session_state:
            pdf = generate_pdf(
                st.session_state["data"],
                st.session_state.get("root"),
                st.session_state.get("l2"),
                st.session_state.get("res"),
                st.session_state.get("images")
            )
            st.sidebar.download_button("Download PDF", pdf, "report.pdf")

    if st.sidebar.button("Generate Word", use_container_width=True):
        if "data" in st.session_state:
            doc = generate_word_doc(
                st.session_state["data"],
                st.session_state.get("root"),
                st.session_state.get("l2"),
                st.session_state.get("res"),
                st.session_state.get("images")
            )
            st.sidebar.download_button("Download Word", doc, "report.docx")

    return filtered
