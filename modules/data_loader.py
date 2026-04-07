import pandas as pd
import streamlit as st
from config import CONFIG, ENV

# --------------------------------------------------
# SAFE COLUMN GETTER
# --------------------------------------------------
def safe_col(df, col):
    for c in df.columns:
        if c.lower().strip() == col.lower():
            return df[c]
    return pd.Series([None] * len(df))

# --------------------------------------------------
# FILE READER
# --------------------------------------------------
def read_file(url):
    if url.endswith(".csv"):
        return pd.read_csv(url)
    elif url.endswith(".xlsx"):
        return pd.read_excel(url)
    else:
        raise ValueError(f"Unsupported file format: {url}")

# --------------------------------------------------
# BUILD FUNCTIONS (FIXED)
# --------------------------------------------------

def build_azure(df):
    return pd.DataFrame({
        "Number": safe_col(df, "id"),
        "Description": safe_col(df, "title"),
        "Priority": [None] * len(df),
        "Status": safe_col(df, "state"),
        "Created By": safe_col(df, "created by"),
        "Created Date": safe_col(df, "created date"),
        "Assigned To": safe_col(df, "assigned to"),
        "Resolved Date": safe_col(df, "resolved date"),
        "Release": safe_col(df, "release_windchill"),
        "Source": ["AZURE"] * len(df)
    })


def build_snow(df):
    return pd.DataFrame({
        "Number": safe_col(df, "number"),
        "Description": safe_col(df, "short description"),
        "Priority": safe_col(df, "priority"),
        "Status": safe_col(df, "incident state"),
        "Created By": safe_col(df, "opened by"),
        "Created Date": safe_col(df, "created"),
        "Assigned To": safe_col(df, "assigned to"),
        "Resolved Date": safe_col(df, "resolved"),
        "Release": [None] * len(df),
        "Source": ["SNOW"] * len(df)
    })

import pandas as pd
from config import CONFIG, ENV


def load_data():
    config = CONFIG[ENV]

    all_data = []

    for source, url in config.items():

        try:
            if url.endswith(".csv"):
                df = pd.read_csv(url)
            else:
                df = pd.read_excel(url)

            source_name = source.replace("_URL", "")
            df["Source"] = source_name

            # --- FIX PTC COLUMN MAPPING ---
            if source_name == "PTC":
                df.rename(columns={
                    "Case Number": "Number",
                    "Summary": "Description",
                    "Created On": "Created Date",
                    "Owner": "Assigned To",
                    "Resolution Date": "Resolved Date"
                }, inplace=True)

            # --- STANDARD COLUMN FIX ---
            df.rename(columns={
                "Resolution Date": "Resolved Date"
            }, inplace=True)

            all_data.append(df)

        except Exception as e:
            print(f"Error loading {source}: {e}")

    if not all_data:
        return pd.DataFrame(), {}

    final_df = pd.concat(all_data, ignore_index=True)

    return final_df, {"last_refresh": "Auto"}
    
#def build_ptc(df):
   # return pd.DataFrame({
   #     "Number": safe_col(df, "case number"),
  #      "Description": safe_col(df, "subject"),
  #      "Priority": safe_col(df, "severity"),
  #      "Status": safe_col(df, "status"),
 #       "Created By": safe_col(df, "case contact"),
   #     "Created Date": safe_col(df, "created date"),
  #     "Assigned To": safe_col(df, "case assignee"),
     #   "Resolved Date": safe_col(df, "resolved date"),
    #    "Release": [None] * len(df),
   #     "Source": ["PTC"] * len(df)
#    })

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data(ttl=300)
def load_data():
    try:
        urls = CONFIG[ENV]

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
