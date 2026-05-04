import streamlit as st
import os
import sys

# Ensure root path is available
sys.path.append(os.path.abspath("."))

# Existing modules
from modules.search.search_ui import render as search_ui
from modules.analytics.charts_page import render as analytics_ui
from modules.report.doc_generator_ui import render_doc_generator as report_ui
from modules.excel_compare.ui import render as excel_compare_ui
from modules.converter.converter_ui import render as converter_ui

# New Word Compare module
from modules.word_compare.ui import render as word_compare_ui


# ----------------------------
# Streamlit Config
# ----------------------------
st.set_page_config(
    page_title="Utility Dashboard",
    layout="wide"
)


# ----------------------------
# Sidebar Navigation
# ----------------------------
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Home",
        "Search",
        "Analytics",
        "Report",
        "Excel Compare",
        "Word Compare",
        "Converter"
    ]
)


# ----------------------------
# Page Routing
# ----------------------------
if page == "Home":
    st.title("🏠 Home")
    st.write("Welcome! Select a utility from the sidebar.")

elif page == "Search":
    search_ui()

elif page == "Analytics":
    analytics_ui()

elif page == "Report":
    report_ui()

elif page == "Excel Compare":
    excel_compare_ui()

elif page == "Word Compare":
    word_compare_ui()

elif page == "Converter":
    converter_ui()
