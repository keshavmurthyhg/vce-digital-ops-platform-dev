import pandas as pd
import streamlit as st
import requests
from io import BytesIO
from config import CONFIG, ENV

REFRESH_INTERVAL = 300


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
            st.warning(f"⚠️ Failed file: {url}")
            return None, None

    except Exception as e:
        st.error(f"❌ Fetch error: {e}")
        return None, None


def read_file(content, url):
    try:
        if url.endswith(".csv"):
            return pd.read_csv(BytesIO(content))
        else:
            return pd.read_excel(BytesIO(content))
    except Exception:
        try:
            return pd.read_csv(BytesIO(content))
        except:
            return pd.DataFrame()


# -------------------------------
# TRANSFORMATIONS
# -------------------------------
def build_azure(df):
    df = normalize_columns(df)

    return pd.DataFrame({
        "Number": get_col(df, "id"),
        "Description": get_col(df, "title"),
        "Priority": get_col(df, "priority"),
        "Status": get_col(df, "state"),
        "Created By": get_col(df, "created by"),
        "Created Date": get_col(df, "created date"),
        "Assigned To": get_col(df, "assigned to"),
        "Resolved Date": get_col(df, "resolved date"),
        "Release": get_col(df, "release_windchill"),
        "Source": "AZURE"
    })


def build_snow(df):
    df = normalize_columns(df)

    return pd.DataFrame({
        "Number": get_col(df, "number"),
        "Description": get_col(df, "short description"),
        "Priority": get_col(df, "priority"),
        "Status": get_col(df, "incident state"),
        "Created By": get_col(df, "opened by"),
        "Created Date": get_col(df, "created date", "created"),
        "Assigned To": get_col(df, "assigned to"),
        "Resolved Date": get_col(df, "resolved"),
        "Release": None,
        "Source": "SNOW"
    })


def build_ptc(df):
    df = normalize_columns(df)

    # DEBUG (remove later if needed)
    # st.write("PTC Columns:", df.columns)

    return pd.DataFrame({
        "Number": df.get("case number"),
        "Description": df.get("subject"),
        "Priority": df.get("severity"),
        "Status": df.get("status"),
        "Created By": df.get("case contact"),
        "Created Date": df.get("created date"),
        "Assigned To": df.get("case assignee"),
        "Resolved Date": df.get("resolved date"),
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

    # --- SNOW ---
    snow_content, snow_headers = fetch_file(urls["SNOW_URL"])
    if snow_content:
        df_snow = build_snow(read_file(snow_content, urls["SNOW_URL"]))
        data_info["SNOW"] = snow_headers.get("Last-Modified", "Updated")
    else:
        df_snow = pd.DataFrame()
        data_info["SNOW"] = "FAILED"

    # --- PTC ---
    ptc_content, ptc_headers = fetch_file(urls["PTC_URL"])
    if ptc_content:
        df_ptc = build_ptc(read_file(ptc_content, urls["PTC_URL"]))
        data_info["PTC"] = ptc_headers.get("Last-Modified", "Updated")
    else:
        df_ptc = pd.DataFrame()
        data_info["PTC"] = "FAILED"

    # --- AZURE ---
    azure_content, azure_headers = fetch_file(urls["AZURE_URL"])
    if azure_content:
        df_azure = build_azure(read_file(azure_content, urls["AZURE_URL"]))
        data_info["AZURE"] = azure_headers.get("Last-Modified", "Updated")
    else:
        df_azure = pd.DataFrame()
        data_info["AZURE"] = "FAILED"

    # --- COMBINE ---
    df = pd.concat([df_snow, df_ptc, df_azure], ignore_index=True)

    return df, data_info
