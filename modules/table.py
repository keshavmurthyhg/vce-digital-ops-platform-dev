import streamlit as st
import pandas as pd
import re


def clean_name(val):
    if pd.isna(val):
        return val
    val = str(val)
    val = re.sub(r"\s*<.*?>", "", val)
    val = re.sub(r"\s*\(.*?\)", "", val)
    return val.strip()


def build_link(row):
    num = str(row.get("Number", ""))
    src = row.get("Source", "")

    if src == "SNOW":
        return f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={num}"
    elif src == "PTC":
        return f"https://support.ptc.com/appserver/cs/view/case.jsp?n={num}"
    elif src == "AZURE":
        return f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{num}"
    return ""


def show_table(df):

    if df.empty:
        st.warning("No data")
        return

    df = df.copy().reset_index(drop=True)
    df.insert(0, "SL No", df.index + 1)

    # Clean names
    for col in ["Created By", "Assigned To"]:
        if col in df.columns:
            df[col] = df[col].apply(clean_name)

    # Format dates
    for col in ["Created Date", "Resolved Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%d-%b-%y")

    # Remove .0 issue
    if "Assigned To" in df.columns:
        df["Assigned To"] = df["Assigned To"].astype(str).str.replace(".0", "", regex=False)

    # Link column
    df["Open"] = df.apply(build_link, axis=1)

    # Column order
    cols = [
        "SL No", "Number", "Description", "Priority", "Status",
        "Created By", "Created Date", "Assigned To",
        "Resolved Date", "Source", "Open"
    ]
    df = df[[c for c in cols if c in df.columns]]

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Open": st.column_config.LinkColumn("🔗"),
            "Description": st.column_config.TextColumn(width="large"),
        }
    )
