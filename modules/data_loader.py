import pandas as pd
import streamlit as st
import requests
from io import BytesIO
from config import CONFIG, ENV

REFRESH_INTERVAL = 300


# ---------------------------------
# FETCH FILE
# ---------------------------------
def fetch_file(url):
    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200 and len(r.content) > 100:
            return r.content
        else:
            st.warning(f"⚠️ Failed to load: {url}")
            return None
    except Exception as e:
        st.error(f"❌ Fetch error: {e}")
        return None


# ---------------------------------
# READ FILE
# ---------------------------------
def read_file(content, url):
    try:
        if url.endswith(".csv"):
            return pd.read_csv(BytesIO(content))
        else:
            return pd.read_excel(BytesIO(content))
    except Exception:
        return pd.DataFrame()


# ---------------------------------
# NORMALIZE COLUMN NAMES
# ---------------------------------
def normalize_columns(df):
    df.columns = (
        df.columns.astype(str)
        .str.replace("\n", " ")
        .str.strip()
        .str.lower()
    )
    return df


# ---------------------------------
# SAFE COLUMN FETCH
# ---------------------------------
def safe_get(df, name):
    return df[name] if name in df.columns else pd.Series([None]*len(df))


# ---------------------------------
# AZURE
# ---------------------------------
def build_azure(df):
    df = normalize_columns(df)

    return pd.DataFrame({
        "Number": safe_get(df, "id"),
        "Description": safe_get(df, "title"),
        "Priority": safe_get(df, "priority"),
        "Status": safe_get(df, "state"),
        "Created By": safe_get(df, "created by"),
        "Created Date": safe_get(df, "created date"),
        "Assigned To": safe_get(df, "assigned to"),
        "Resolved Date": safe_get(df, "resolved date"),
        "Release": safe_get(df, "release_windchill"),
        "Source": "AZURE"
    })


# ---------------------------------
# SNOW
# ---------------------------------
def build_snow(df):
    df = normalize_columns(df)

    return pd.DataFrame({
        "Number": safe_get(df, "number"),
        "Description": safe_get(df, "short description"),
        "Priority": safe_get(df, "priority"),
        "Status": safe_get(df, "incident state"),
        "Created By": safe_get(df, "opened by"),
        "Created Date": safe_get(df, "created date"),
        "Assigned To": safe_get(df, "assigned to"),
        "Resolved Date": safe_get(df, "resolved"),
        "Release": pd.Series([None]*len(df)),
        "Source": "SNOW"
    })


# ---------------------------------
# PTC (FINAL ROBUST VERSION)
# ---------------------------------
def build_ptc(df):

    if df.empty:
        return df

    # -------------------------------
    # NORMALIZE COLUMN NAMES
    # -------------------------------
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.upper()
    )

    # -------------------------------
    # DEBUG (REMOVE AFTER TEST)
    # -------------------------------
    st.write("PTC Columns:", df.columns.tolist())

    # -------------------------------
    # SIMPLE DIRECT MAPPING (LIKE SNOW)
    # -------------------------------
    return pd.DataFrame({
        "Number": df.get("CASE NUMBER"),
        "Description": df.get("SUBJECT"),
        "Priority": df.get("SEVERITY"),
        "Status": df.get("STATUS"),
        "Created By": df.get("CASE CONTACT"),
        "Created Date": df.get("CREATED DATE"),
        "Assigned To": df.get("CASE ASSIGNEE"),
        "Resolved Date": df.get("RESOLVED DATE"),
        "Release": None,
        "Source": "PTC"
    })

# ---------------------------------
# LOAD DATA
# ---------------------------------
@st.cache_data(ttl=REFRESH_INTERVAL)
def load_data():

    urls = CONFIG[ENV]

    snow = fetch_file(urls["SNOW_URL"])
    ptc = fetch_file(urls["PTC_URL"])
    azure = fetch_file(urls["AZURE_URL"])

    df_snow = build_snow(read_file(snow, urls["SNOW_URL"])) if snow else pd.DataFrame()
    df_ptc = build_ptc(read_file(ptc, urls["PTC_URL"])) if ptc else pd.DataFrame()
    df_azure = build_azure(read_file(azure, urls["AZURE_URL"])) if azure else pd.DataFrame()

    df = pd.concat([df_snow, df_ptc, df_azure], ignore_index=True)

    return df, {}
