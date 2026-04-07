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


# --- Build URL ---
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

df["Open"] = df.apply(
    lambda x: f'<a href="{build_link(x)}" target="_blank">🔗</a>',
    axis=1
)


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

    # --- Build Links ---
    df["Open"] = df.apply(build_link, axis=1)

    # --- Table Styling ---
    st.markdown("""
    <style>
    [data-testid="stDataFrame"] th,
    [data-testid="stDataFrame"] td {
        text-align: center !important;
        vertical-align: middle !important;
        font-size: 12px;
    }

    /* Left align text-heavy columns */
    [data-testid="stDataFrame"] td:nth-child(4),
    [data-testid="stDataFrame"] td:nth-child(8),
    [data-testid="stDataFrame"] td:nth-child(9) {
        text-align: left !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Display ---
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Open": st.column_config.LinkColumn("Open Link"),
            "SL No": st.column_config.NumberColumn(width="small"),
            "Description": st.column_config.TextColumn(width="large"),
        }
    )
