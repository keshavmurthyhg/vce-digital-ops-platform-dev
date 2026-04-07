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

    # -------------------------------
    # STEP 1: FIND HEADER ANYWHERE
    # -------------------------------
    header_row = None

    for i in range(len(df)):
        row = df.iloc[i].astype(str).str.lower().tolist()

        if "case number" in row and "subject" in row:
            header_row = i
            break

    # -------------------------------
    # STEP 2: APPLY HEADER
    # -------------------------------
    if header_row is not None:
        df.columns = df.iloc[header_row]
        df = df[(header_row + 1):]
    else:
        st.error("❌ PTC header not found")
        return pd.DataFrame()

    # -------------------------------
    # STEP 3: CLEAN COLUMNS
    # -------------------------------
    df.columns = (
        df.columns.astype(str)
        .str.replace("\n", " ")
        .str.strip()
        .str.lower()
    )

    # -------------------------------
    # STEP 4: DROP EMPTY ROWS
    # -------------------------------
    df = df.dropna(how="all")

    # -------------------------------
    # STEP 5: DEBUG (IMPORTANT)
    # -------------------------------
    st.write("PTC columns detected:", df.columns)

    # -------------------------------
    # STEP 6: EXTRACT COLUMNS SAFELY
    # -------------------------------
    def col(name):
        if name in df.columns:
            return df[name]
        else:
            st.warning(f"Missing column: {name}")
            return pd.Series([None] * len(df))

    return pd.DataFrame({
        "Number": col("case number"),
        "Description": col("subject"),
        "Priority": col("severity"),
        "Status": col("status"),
        "Created By": col("case contact"),
        "Created Date": col("created date"),
        "Assigned To": col("case assignee"),
        "Resolved Date": col("resolved date"),
        "Release": pd.Series([None] * len(df)),
        "Source": pd.Series(["PTC"] * len(df))
    })


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
