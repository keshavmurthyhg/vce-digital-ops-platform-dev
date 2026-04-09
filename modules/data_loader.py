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
    df.columns = (
        df.columns.astype(str)
        .str.replace("\n", " ")
        .str.strip()
        .str.lower()
    )
    return df


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
# BUILDERS
# -------------------------------
def build_azure(df):
    df = normalize_columns(df)

    def col(name):
        return df[name] if name in df.columns else pd.Series([None]*len(df))

    return pd.DataFrame({
        "Number": col("id"),
        "Description": col("title"),
        "Priority": col("priority"),
        "Status": col("state"),
        "Created By": col("created by"),
        "Created Date": col("created date"),
        "Assigned To": col("assigned to"),
        "Resolved Date": col("resolved date"),
        "Release": col("release_windchill"),
        "Source": "AZURE"
    })


def build_snow(df):
    df = normalize_columns(df)

    def col(name):
        return df[name] if name in df.columns else pd.Series([None]*len(df))

    return pd.DataFrame({
        "Number": col("number"),
        "Description": col("short description"),
        "Priority": col("priority"),
        "Status": col("incident state"),
        "Created By": col("opened by"),
        "Created Date": col("created date"),
        "Assigned To": col("assigned to"),
        "Resolved Date": col("resolved"),
        "Release": pd.Series([None]*len(df)),
        "Source": "SNOW"
    })


def build_ptc(df):

    df = df.copy()

    # -------------------------------
    # SAFE STRING CONVERSION
    # -------------------------------
    df_safe = df.fillna("").astype(str)

    # -------------------------------
    # FIND HEADER ROW (SAFE)
    # -------------------------------
    header_row = None

    for i in range(len(df_safe)):
        row = " ".join([str(x).lower() for x in df_safe.iloc[i].tolist()])

        if "case" in row and "subject" in row:
            header_row = i
            break

    if header_row is None:
        st.error("❌ PTC header not found")
        st.write("Preview:", df.head(5))
        return pd.DataFrame()

    # -------------------------------
    # APPLY HEADER
    # -------------------------------
    df.columns = df.iloc[header_row]
    df = df[(header_row + 1):]

    # -------------------------------
    # CLEAN COLUMN NAMES
    # -------------------------------
    df.columns = (
        df.columns.astype(str)
        .str.lower()
        .str.replace(r"[^a-z0-9 ]", "", regex=True)
        .str.strip()
    )

    df = df.dropna(how="all")

    # -------------------------------
    # SAFE COLUMN FINDER
    # -------------------------------
    def find_col(keywords):
        for col in df.columns:
            if all(k in col for k in keywords):
                return df[col]
        return pd.Series([None] * len(df))

    # -------------------------------
    # BUILD FINAL DATA
    # -------------------------------
    result = pd.DataFrame({
        "Number": find_col(["case", "number"]),
        "Description": find_col(["subject"]),
        "Priority": find_col(["severity"]),
        "Status": find_col(["status"]),
        "Created By": find_col(["contact"]),
        "Created Date": find_col(["created"]),
        "Assigned To": find_col(["assignee"]),
        "Resolved Date": find_col(["resolved"]),
        "Release": pd.Series([None] * len(df)),
        "Source": pd.Series(["PTC"] * len(df))
    })

    return result


# -------------------------------
# MAIN LOADER
# -------------------------------
@st.cache_data(ttl=REFRESH_INTERVAL)
def load_data():

    urls = CONFIG[ENV]
    data_info = {}

    # SNOW
    snow_content, snow_headers = fetch_file(urls["SNOW_URL"])
    df_snow = build_snow(read_file(snow_content, urls["SNOW_URL"])) if snow_content else pd.DataFrame()

    # PTC
    ptc_content, ptc_headers = fetch_file(urls["PTC_URL"])
    df_ptc = build_ptc(read_file(ptc_content, urls["PTC_URL"])) if ptc_content else pd.DataFrame()

    # AZURE
    azure_content, azure_headers = fetch_file(urls["AZURE_URL"])
    df_azure = build_azure(read_file(azure_content, urls["AZURE_URL"])) if azure_content else pd.DataFrame()

    df = pd.concat([df_snow, df_ptc, df_azure], ignore_index=True)

    return df, data_info
