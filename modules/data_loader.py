import pandas as pd

# -------------------------------
# NORMALIZE COLUMN NAMES
# -------------------------------
def norm(df):
    df.columns = df.columns.astype(str).str.strip().str.lower()
    return df


# -------------------------------
# SAFE COLUMN FETCH
# -------------------------------
def col(df, *names):
    for n in names:
        if n in df.columns:
            return df[n]
    return None


# -------------------------------
# AZURE
# -------------------------------
def build_azure(df):
    return pd.DataFrame({
        "Number": col(df, "id"),
        "Description": col(df, "title"),
        "Priority": col(df, "release_windchill"),
        "Status": col(df, "state"),
        "Created By": col(df, "created by"),
        "Created Date": col(df, "created date"),
        "Assigned To": col(df, "assigned to"),
        "Resolved Date": col(df, "resolved date"),
        "Source": "AZURE"
    })


# -------------------------------
# SNOW (FIXED)
# -------------------------------
def build_snow(df):
    return pd.DataFrame({
        "Number": col(df, "number"),
        "Description": col(df, "short description", "description"),
        "Priority": col(df, "priority"),
        "Status": col(df, "incident state"),
        "Created By": col(df, "opened by", "created by"),
        "Created Date": col(df, "created", "date"),
        "Assigned To": col(df, "assigned to"),
        "Resolved Date": col(df, "resolved"),
        "Source": "SNOW"
    })


# -------------------------------
# PTC (FIXED)
# -------------------------------
def build_ptc(df):
    return pd.DataFrame({
        "Number": col(df, "case number"),
        "Description": col(df, "subject"),
        "Priority": col(df, "severity"),
        "Status": col(df, "status"),
        "Created By": col(df, "case contact"),
        "Created Date": col(df, "created date"),
        "Assigned To": col(df, "case assignee"),
        "Resolved Date": col(df, "resolved date"),
        "Source": "PTC"
    })


# -------------------------------
# LOAD DATA
# -------------------------------
def load_data():

    try:
        azure = pd.read_csv("data/Azure.csv")

        snow = pd.read_excel(
            "data/Snow.xlsx",
            engine="openpyxl"
        )

        ptc = pd.read_csv(
            "data/Ptc.csv",
            index_col=False,
            engine="python"
        )

        ptc = ptc.reset_index(drop=True)

    except Exception as e:
        import streamlit as st
        st.error(f"❌ Data load failed: {e}")
        return pd.DataFrame(), {}

    azure = norm(azure)
    snow = norm(snow)
    ptc = norm(ptc)

    df = pd.concat([
        build_azure(azure),
        build_snow(snow),
        build_ptc(ptc)
    ], ignore_index=True)

    df = df.reset_index(drop=True)
    df = df.fillna("")

    from datetime import datetime
    info = datetime.now().strftime("%d-%b-%Y %H:%M")

    return df, info
