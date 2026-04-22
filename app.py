import streamlit as st
from modules.search.search_ui import render as search_ui

st.set_page_config(layout="wide")

st.sidebar.title("Navigation")

page = st.sidebar.radio("Go to", ["Home", "Search"])

if page == "Home":
    st.title("🏠 Home")
    st.write("Select module")

elif page == "Search":
    search_ui()
