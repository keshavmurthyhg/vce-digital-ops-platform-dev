import streamlit as st

# Import module UI entry points
from modules.search.search_page import render as search_ui
from modules.analytics.charts_page import render as analytics_ui
from modules.report.doc_generator_ui import render as report_ui

st.set_page_config(page_title="Dashboard", layout="wide")

# Sidebar navigation
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    ["Home", "Search", "Analytics", "Report"]
)

# Routing
if page == "Home":
    st.title("🏠 Home")
    st.write("Welcome! Select a module from the sidebar.")

elif page == "Search":
    search_ui()

elif page == "Analytics":
    analytics_ui()

elif page == "Report":
    report_ui()
