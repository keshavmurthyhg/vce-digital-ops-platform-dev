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

    if df is None or df.empty:
        st.warning("No data available")
        return

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

    # --- Build Links ---
    df["Open"] = df.apply(build_link, axis=1)

    # --- Replace NaN (CRITICAL FIX) ---
    df = df.fillna("")

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

    /* Left align Description */
    tbody td:nth-child(3) {
        text-align: left;
    }

    tbody tr:hover {
        background-color: #f9f9f9;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Render table (SAFE) ---
    try:
        html = df.to_html(
            index=False,
            escape=False,
            render_links=True
        )
        st.markdown(html, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Table rendering failed: {e}")
