import streamlit as st
from .logic import load_data, process_data

def render():
    st.title("🔍 Search Dashboard")

    uploaded_file = st.file_uploader("Upload File")

    if uploaded_file:
        data = load_data(uploaded_file)
        result = process_data(data)

        st.write(result)
