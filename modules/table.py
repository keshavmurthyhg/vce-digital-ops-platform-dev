import streamlit as st
import pandas as pd
import re


def clean_name(value):
    """Remove email IDs (<...>) and extra brackets safely"""
    try:
        if pd.isna(value):
            return value

        value = str(value)

        # Remove email inside <>
        value = re.sub(r"\s*<.*?>", "", value)

        # Optional: remove (2), (1), etc.
        value = re.sub(r"\s*\(.*?\)", "", value)

        return value.strip()

    except Exception:
        return value


def show_table(df):

    # --- Safety copy (prevents modifying original data) ---
    df = df.copy()

    # --- Add SL No ---
    df = df.reset_index(drop=True)
    df.insert(0, "SL No", df.index + 1)

    # --- Clean Name Columns ---
    cols_to_clean = ["Created By", "Assigned To"]
    for col in cols_to_clean:
        if col in df.columns:
            df[col] = df[col].apply(clean_name)

    # --- Date Formatting ---
    date_cols = ["Created Date", "Resolution Date"]
    for col in date_cols:
        if col in df.columns:
            df[col] = (
                pd.to_datetime(df[col], errors="coerce")
                .dt.strftime("%d-%b-%y")
            )

    # --- Vertical + Horizontal Alignment CSS ---
    st.markdown("""
    <style>
    /* Center everything */
    [data-testid="stDataFrame"] th,
    [data-testid="stDataFrame"] td {
        display: flex;
        align-items: center !important;
        justify-content: center;
    }

    /* Left align specific columns */
    [data-testid="stDataFrame"] td:nth-child(4),
    [data-testid="stDataFrame"] td:nth-child(8),
    [data-testid="stDataFrame"] td:nth-child(9) {
        justify-content: flex-start !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
<style>
/* Enable tooltip on hover */
[data-testid="stDataFrame"] td {
    position: relative;
}

/* Tooltip */
[data-testid="stDataFrame"] td:hover::after {
    content: attr(title);
    position: absolute;
    left: 0;
    top: 100%;
    background: #333;
    color: #fff;
    padding: 6px 10px;
    border-radius: 6px;
    white-space: pre-wrap;
    z-index: 9999;
    min-width: 200px;
    max-width: 500px;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)    
    
    # --- Display Table ---
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "SL No": st.column_config.NumberColumn(width="small"),
            "Description": st.column_config.TextColumn(width="large"),
        }
    )

