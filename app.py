import streamlit as st

from modules.search.search_ui import render as search_ui
from modules.analytics.charts_page import render as analytics_ui

st.set_page_config(layout="wide")

st.sidebar.title("Navigation")

page = st.sidebar.radio("Go to", ["Home", "Search", "Analytics"])

if page == "Home":
    st.title("🏠 Home")
    st.write("Welcome! Select a module.")

elif page == "Search":
    search_ui()

elif page == "Analytics":
    analytics_ui()
