import streamlit as st
from modules.data_loader import load_snow_data

from ui.state import init_state
from ui.sidebar import render_sidebar
from ui.main_view import render_main

def main():
    init_state()

    df = load_snow_data()

    filtered = render_sidebar(df)

    st.session_state.filtered_df = filtered

    render_main(filtered)

if __name__ == "__main__":
    main()
