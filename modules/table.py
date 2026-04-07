import streamlit as st
import pandas as pd
import re


def clean_name(value):
    try:
        if pd.isna(value):
            return value

        value = str(value)
        value = re.sub(r"\s*<.*?>", "", value)
        value = re.sub(r"\s*\(.*?\)", "", value)
        return value.strip()

    except Exception:
        return value


def build_link(row):
    number = str(row.get("Number", ""))
    source = str(row.get("Source", "")).upper()

    if source == "SNOW":
        return f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={number}"

    elif source == "PTC":
        return f"https://support.ptc.com/appserver/cs/view/case.jsp?n={number}"

    elif source == "AZURE":
        return f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{number}"

    return ""


def show_table(df):

    # --- Copy ---
    df = df.copy()

    # --- SL No ---
    df = df.reset_index(drop=True)
    df.insert(0, "SL No", df.index + 1)

    # --- Clean Names ---
    for col in ["Created By", "Assigned To"]:
        if col in df.columns:
            df[col] = df[col].apply(clean_name)

    # --- Date Format ---
    for col in ["Created Date", "Resolved Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%d-%b-%y")

    # --- Create Icon Link ---
    df["Open"] = df.apply(
        lambda x: f'<a href="{build_link(x)}" target="_blank">🔗</a>',
        axis=1
    )

    # --- Styling ---
    st.markdown("""
    <style>
    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
    }

    thead th {
        background-color: #f0f2f6;
        padding: 8px;
        text-align: center;
    }

    tbody td {
        padding: 8px;
        border-bottom: 1px solid #ddd;
        text-align: center;
        vertical-align: middle;
    }

    /* Left align description */
    tbody td:nth-child(3) {
        text-align: left;
    }

    /* Hover */
    tbody tr:hover {
        background-color: #f9f9f9;
    }

    a {
        text-decoration: none;
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Display HTML table (needed for clickable icon) ---
    st.markdown(
        df.to_html(escape=False, index=False),
        unsafe_allow_html=True
    )
