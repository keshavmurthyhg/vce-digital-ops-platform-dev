import streamlit as st

def show_kpi(df):
    total = len(df)
    open_ = len(df[df["Status"] == "Open"])

    st.markdown(
        """
        <style>
        .kpi-box {font-size:14px;}
        .kpi-value {font-size:20px; font-weight:600;}
        </style>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"<div class='kpi-box'>Total<br><span class='kpi-value'>{total}</span></div>",
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"<div class='kpi-box'>Open<br><span class='kpi-value'>{open_}</span></div>",
            unsafe_allow_html=True
        )
