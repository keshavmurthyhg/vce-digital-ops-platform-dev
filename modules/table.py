import streamlit as st
import pandas as pd
import re
from st_aggrid import AgGrid, GridOptionsBuilder


def clean_name(value):
    """Remove email IDs (<...>) and extra brackets safely"""
    try:
        if pd.isna(value):
            return value

        value = str(value)

        # Remove email inside <>
        value = re.sub(r"\s*<.*?>", "", value)

        # Remove (1), (2), etc.
        value = re.sub(r"\s*\(.*?\)", "", value)

        return value.strip()

    except Exception:
        return value


def show_table(df):

    # --- Safety copy ---
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

    # --- Build AgGrid ---
    gb = GridOptionsBuilder.from_dataframe(df)

    # Enable tooltip for ALL columns
    for col in df.columns:
        gb.configure_column(col, tooltipField=col)

    # Default center alignment (vertical + horizontal)
    gb.configure_default_column(
        resizable=True,
        sortable=True,
        filter=True,
        cellStyle={
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center"
        }
    )

    # Left align specific columns
    for col in ["Description", "Assigned To", "Created By", "Resolved By"]:
        if col in df.columns:
            gb.configure_column(col, cellStyle={"justifyContent": "flex-start"})

    # Optional: better column widths
    gb.configure_column("SL No", maxWidth=90)
    if "Description" in df.columns:
        gb.configure_column("Description", flex=2)

    gridOptions = gb.build()

    # --- Display Grid ---
    AgGrid(
        df,
        gridOptions=gridOptions,
        fit_columns_on_grid_load=True,
        enable_enterprise_modules=False,
        height=500,
        theme="streamlit"
    )
