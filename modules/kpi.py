import streamlit as st

def show_kpi(df):
    total = len(df)
    open_ = len(df[df["Status"] == "Open"])
    closed = len(df[df["Status"] == "Closed"])
    cancelled = len(df[df["Status"] == "Cancelled"])

    st.markdown("""
    <style>
    .kpi-box {font-size:13px;}
    .kpi-value {font-size:18px; font-weight:600;}
    </style>
    """, unsafe_allow_html=True)

    col1, col2, = st.columns(2)

    col1.markdown(f"<div class='kpi-box'>Total<br><span class='kpi-value'>{total}</span></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='kpi-box'>Open<br><span class='kpi-value'>{open_}</span></div>", unsafe_allow_html=True)
    col1.markdown(f"<div class='kpi-box'>Closed<br><span class='kpi-value'>{closed}</span></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='kpi-box'>Cancelled<br><span class='kpi-value'>{cancelled}</span></div>", unsafe_allow_html=True)
