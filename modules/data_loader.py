import pandas as pd
import streamlit as st
import requests
from io import BytesIO
from config import CONFIG, ENV

REFRESH_INTERVAL = 300  # 5 mins


# -------------------------------
# HELPERS
# -------------------------------
def normalize_columns(df):
    df.columns = df.columns.str.strip().str.lower()
    return df


def get_col(df, *cols):
    for col in cols:
        if col in df.columns:
            return df[col]
    return None


def fetch_file(url):
    try:
        response = requests.get(url, timeout=30)

        if response.status_code == 200 and len(response.content) > 100:
            return response.content, response.headers
        else:
            st.warning(f"⚠️ Failed or empty file: {url}")
            return None, None

    except Exception as e:
        st.error(f"❌ Error fetching file: {e}")
        return None, None


def read_file(content, url):
    """
    Smart reader: handles csv/excel automatically
    """
    try:
        if url.endswith(".csv"):
            return pd.read_csv(BytesIO(content))
        else:
            return pd.read_excel(BytesIO(content))
    except Exception:
        try:
            return pd.read_csv(BytesIO(content))
        except Exception:
            return pd.DataFrame()


# -------------------------------
# TRANSFORMATIONS
# -------------------------------
def build_azure(df):
    df = normalize_columns(df)

    return pd.DataFrame({
        "Number": get_col(df, "id"),
        "Description": get_col(df, "title", "system.title"),
        "Status": get_col(df, "state", "system.state"),
        "Priority": get_col(df, "priority"),
        "Created By": get_col(df, "created by", "system.createdby"),
        "Created Date": get_col(df, "created date", "system.createddate"),
        "Assigned To": get_col(df, "assigned to", "system.assignedto"),
        "Resolved Date": get_col(df, "resolved date", "closed date", "system.closeddate"),
        "Release": get_col(df, "release_windchill"),
        "Source": "AZURE"
    })


def build_snow(df):
    df = normalize_columns(df)

    return pd.DataFrame({
        "Number": get_col(df, "number"),
        "Description": get_col(df, "short description"),
        "Status": get_col(df, "incident state", "state"),
        "Priority": get_col(df, "priority"),
        "Created By": get_col(df, "opened by", "caller"),
        "Created Date": get_col(df, "created", "opened"),
        "Assigned To": get_col(df, "assigned to"),
        "Resolved Date": get_col(df, "resolved", "closed"),
        "Release": None,
        "Source": "SNOW"
    })


def build_ptc(df):
    df = normalize_columns(df)

    return pd.DataFrame({
        "Number": get_col(df, "case number"),
        "Description": get_col(df, "subject"),
        "Status": get_col(df, "status"),
        "Priority": get_col(df, "severity"),
        "Created By": get_col(df, "case contact"),
        "Created Date": get_col(df, "created date"),
        "Assigned To": get_col(df, "case assignee"),
        "Resolved Date": get_col(df, "resolved date"),
        "Release": None,
        "Source": "PTC"
    })


# -------------------------------
# MAIN LOADER
# -------------------------------
@st.cache_data(ttl=REFRESH_INTERVAL)
def load_data():

    urls = CONFIG[ENV]
    data_info = {}

    # -------- SNOW --------
    snow_content, snow_headers = fetch_file(urls["SNOW_URL"])

    if snow_content:
        try:
            df_snow_raw = read_file(snow_content, urls["SNOW_URL"])
            df_snow = build_snow(df_snow_raw)
            data_info["SNOW"] = snow_headers.get("Last-Modified", "Updated")
        except Exception as e:
            st.error(f"❌ SNOW error: {e}")
            df_snow = pd.DataFrame()
            data_info["SNOW"] = "FAILED"
    else:
        df_snow = pd.DataFrame()
        data_info["SNOW"] = "FAILED"

    # -------- PTC --------
    ptc_content, ptc_headers = fetch_file(urls["PTC_URL"])

    if ptc_content:
        try:
            df_ptc_raw = read_file(ptc_content, urls["PTC_URL"])
            df_ptc = build_ptc(df_ptc_raw)
            data_info["PTC"] = ptc_headers.get("Last-Modified", "Updated")
        except Exception as e:
            st.error(f"❌ PTC error: {e}")
            df_ptc = pd.DataFrame()
            data_info["PTC"] = "FAILED"
    else:
        df_ptc = pd.DataFrame()
        data_info["PTC"] = "FAILED"

    # -------- AZURE --------
    azure_content, azure_headers = fetch_file(urls["AZURE_URL"])

    if azure_content:
        try:
            df_azure_raw = read_file(azure_content, urls["AZURE_URL"])
            df_azure = build_azure(df_azure_raw)
            data_info["AZURE"] = azure_headers.get("Last-Modified", "Updated")
        except Exception as e:
            st.error(f"❌ AZURE error: {e}")
            df_azure = pd.DataFrame()
            data_info["AZURE"] = "FAILED"
    else:
        df_azure = pd.DataFrame()
        data_info["AZURE"] = "FAILED"

    # -------- COMBINE --------
    df = pd.concat([df_snow, df_ptc, df_azure], ignore_index=True)

    # -------- FINAL COLUMN ORDER --------
    final_columns = [
        "Number",
        "Description",
        "Priority",
        "Status",
        "Created By",
        "Created Date",
        "Assigned To",
        "Resolved Date",
        "Release",
        "Source"
    ]

    df = df.reindex(columns=final_columns)

    return df, data_info
