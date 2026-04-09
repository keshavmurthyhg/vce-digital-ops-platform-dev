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
        response = requests.get(url, timeout=30)

        if response.status_code == 200 and len(response.content) > 100:
            return response.content
        else:
            st.warning(f"⚠️ Failed to load: {url}")
            return None

    except Exception as e:
        st.error(f"❌ Error fetching file: {e}")
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
# NORMALIZE
# ---------------------------------
def normalize_columns(df):
    df.columns = (
        df.columns.astype(str)
        .fillna("")
        .str.replace("\n", " ")
        .str.strip()
        .str.lower()
    )
    return df


# ---------------------------------
# AZURE
# ---------------------------------
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


# ---------------------------------
# SNOW
# ---------------------------------
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


# ---------------------------------
# SAFE COLUMN FINDER
# ---------------------------------
def find_col(df, keywords):
    for col in df.columns:
        col_str = str(col).lower()  # ✅ FORCE STRING HERE

        try:
            if all(k in col_str for k in keywords):
                return df[col]
        except Exception:
            continue  # extra safety

    return pd.Series([None] * len(df))


# ---------------------------------
# PTC (FINAL SAFE)
# ---------------------------------
def build_ptc(df):

    if df.empty:
        return df

    df_safe = df.fillna("").astype(str)

    # -------------------------------
    # FIND HEADER ROW
    # -------------------------------
    header_row = None

    for i in range(len(df_safe)):
        row = " ".join(df_safe.iloc[i].str.lower())

        if "case number" in row and "subject" in row:
            header_row = i
            break

    if header_row is None:
        st.error("❌ PTC header not found")
        st.write(df.head(5))
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
        .str.strip()
        .str.upper()
    )

    df = df.dropna(how="all")

    # -------------------------------
    # EXACT COLUMN MAP (FINAL FIX)
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
