import pandas as pd
import streamlit as st
from config import CONFIG, ENV

# --------------------------------------------------
# FILE READER (AUTO DETECT)
# --------------------------------------------------
def read_file(url):
    if url.endswith(".csv"):
        return pd.read_csv(url)
    elif url.endswith(".xlsx"):
        return pd.read_excel(url)
    else:
        raise ValueError(f"Unsupported file format: {url}")

# --------------------------------------------------
# BUILD FUNCTIONS
# --------------------------------------------------

def build_azure(df):
    return pd.DataFrame({
        "Number": df.get("id"),
        "Description": df.get("title"),
        "Priority": None,
        "Status": df.get("state"),
        "Created By": df.get("created by"),
        "Created Date": df.get("created date"),
        "Assigned To": df.get("assigned to"),
        "Resolution Date": df.get("resolved date"),
        "Release": df.get("release_windchill"),
        "Source": "AZURE"
    })


def build_snow(df):
    return pd.DataFrame({
        "Number": df.get("number"),
        "Description": df.get("short description"),
        "Priority": df.get("priority"),
        "Status": df.get("incident state"),
        "Created By": df.get("opened by"),
        "Created Date": df.get("created"),
        "Assigned To": df.get("assigned to"),
        "Resolution Date": df.get("resolved"),
        "Release": None,
        "Source": "SNOW"
    })


def build_ptc(df):
    return pd.DataFrame({
        "Number": df.get("case number"),
        "Description": df.get("subject"),
        "Priority": df.get("severity"),
        "Status": df.get("status"),
        "Created By": df.get("case contact"),
        "Created Date": df.get("created date"),
        "Assigned To": df.get("case assignee"),
        "Resolution Date": df.get("resolved date"),
        "Release": None,
        "Source": "PTC"
    })

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data(ttl=300)
def load_data():
    try:
        urls = CONFIG[ENV]

        # 🔥 AUTO FILE TYPE HANDLING
        azure_raw = read_file(urls["AZURE_URL"])
        snow_raw = read_file(urls["SNOW_URL"])
        ptc_raw = read_file(urls["PTC_URL"])

        df_azure = build_azure(azure_raw)
        df_snow = build_snow(snow_raw)
        df_ptc = build_ptc(ptc_raw)

        df = pd.concat([df_azure, df_snow, df_ptc], ignore_index=True)

        info = {
            "last_refresh": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "records": len(df)
        }

        return df, info

    except Exception as e:
        st.error(f"❌ Data load failed: {e}")
        return pd.DataFrame(), {}
