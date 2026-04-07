import streamlit as st
import pandas as pd

def show_table(df):

    # --- SL No ---
    df = df.reset_index(drop=True)
    df.insert(0, "SL No", df.index + 1)

    # --- Date Format ---
    date_cols = ["Created Date", "Resolution Date"]
    for col in date_cols:
        if col in df.columns:
            df[col] = (
                df[col].astype(str).str.split(" ").str[0]
            )
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%d-%b-%y")

    # --- Alignment CSS ---
    st.markdown("""
    <style>
    [data-testid="stDataFrame"] td {
        text-align: center;
    }
    [data-testid="stDataFrame"] td:nth-child(4),
    [data-testid="stDataFrame"] td:nth-child(7),
    [data-testid="stDataFrame"] td:nth-child(9) {
        text-align: left !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Table ---
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "SL No": st.column_config.NumberColumn(width="small"),
            "Description": st.column_config.TextColumn(width="large"),
        }
    )
