import streamlit as st
import pandas as pd
import re


def clean_name(value):
    """Remove email IDs (<...>) safely"""
    try:
        if pd.isna(value):
            return value

        value = str(value)
        value = re.sub(r"\s*<.*?>", "", value)   # remove email
        value = re.sub(r"\s*\(.*?\)", "", value) # remove (1), (2)
        return value.strip()

    except Exception:
        return value


def show_table(df):

    # --- Copy to avoid modifying original ---
    df = df.copy()

    # --- SL No ---
    df = df.reset_index(drop=True)
    df.insert(0, "SL No", df.index + 1)

    # --- Clean Name Columns ---
    for col in ["Created By", "Assigned To"]:
        if col in df.columns:
            df[col] = df[col].apply(clean_name)

    # --- Date Formatting ---
    for col in ["Created Date", "Resolution Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%d-%b-%y")

    # --- Convert all values to string (needed for tooltip) ---
    df = df.astype(str)

    # --- Inject title attribute for tooltip ---
    def add_tooltip(val):
        return f'<div title="{val}">{val}</div>'

    styled_df = df.applymap(add_tooltip)

    # --- CSS for alignment + tooltip ---
    st.markdown("""
    <style>
    /* Center align */
    [data-testid="stDataFrame"] td, 
    [data-testid="stDataFrame"] th {
        text-align: center !important;
        vertical-align: middle !important;
    }

    /* Left align specific columns (adjust index if needed) */
    [data-testid="stDataFrame"] td:nth-child(4),
    [data-testid="stDataFrame"] td:nth-child(8),
    [data-testid="stDataFrame"] td:nth-child(9) {
        text-align: left !important;
    }

    /* Tooltip styling */
    [data-testid="stDataFrame"] td div[title] {
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Display Table ---
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True
    )
