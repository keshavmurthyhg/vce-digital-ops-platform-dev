import pandas as pd
import streamlit as st
from config import CONFIG, ENV

# --------------------------------------------------
# STANDARD COLUMN STRUCTURE
# --------------------------------------------------
COLUMNS = [
    "Number",
    "Description",
    "Priority",
    "Status",
    "Created By",
    "Created Date",
    "Assigned To",
    "Resolution Date",
    "Release",
    "Source"
]

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
# CLEAN & STANDARDIZE
# --------------------------------------------------

def standardize(df):
    df = df.copy()

    # Ensure all required columns exist
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = None

    # Convert dates safely
    for col in ["Created Date", "Resolution Date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # Sort latest first
    df = df.sort_values(by="Created Date", ascending=False)

    return df[COLUMNS]

# --------------------------------------------------
# LOAD DATA (MAIN FUNCTION)
# --------------------------------------------------

@st.cache_data(ttl=300)  # Auto refresh every 5 mins
def load_data():
    try:
        urls = CONFIG[ENV]

        # ----------------------------
        # READ DATA FROM GITHUB RAW
        # ----------------------------
        azure_raw = pd.read_csv(urls["AZURE_URL"])
        snow_raw = pd.read_csv(urls["SNOW_URL"])
        ptc_raw = pd.read_csv(urls["PTC_URL"])

        # ----------------------------
        # BUILD DATASETS
        # ----------------------------
        df_azure = build_azure(azure_raw)
        df_snow = build_snow(snow_raw)
        df_ptc = build_ptc(ptc_raw)

        # ----------------------------
        # MERGE
        # ----------------------------
        df = pd.concat([df_azure, df_snow, df_ptc], ignore_index=True)

        # ----------------------------
        # STANDARDIZE
        # ----------------------------
        df = standardize(df)

        # ----------------------------
        # DATA INFO
        # ----------------------------
        info = {
            "last_refresh": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_records": len(df),
            "sources": df["Source"].value_counts().to_dict()
        }

        return df, info

    except Exception as e:
        st.error(f"❌ Data load failed: {e}")
        return pd.DataFrame(columns=COLUMNS), {}
