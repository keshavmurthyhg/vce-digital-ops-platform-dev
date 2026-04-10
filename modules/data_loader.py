import pandas as pd
from datetime import datetime

# ================= HELPER =================
def normalize_columns(df):
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df

def find_col(df, keywords):
    for col in df.columns:
        for key in keywords:
            if key in col:
                return col
    return None

def safe_get(df, keywords):
    col = find_col(df, keywords)
    return df[col] if col else ""

# ================= MAIN =================
def load_data():

    # ================= AZURE =================
    azure = pd.read_csv("data/Azure.csv")
    azure = normalize_columns(azure)

    df_azure = pd.DataFrame({
        "Number": safe_get(azure, ["id"]),
        "Description": safe_get(azure, ["title", "description"]),
        "Priority": safe_get(azure, ["priority", "release"]),
        "Status": safe_get(azure, ["state", "status"]),
        "Created By": safe_get(azure, ["created by"]),
        "Created Date": safe_get(azure, ["created date"]),
        "Assigned To": safe_get(azure, ["assigned to"]),
        "Resolved Date": safe_get(azure, ["resolved"]),
        "Source": "AZURE"
    })

    # ================= SNOW =================
    snow = pd.read_excel("data/Snow.xlsx")
    snow = normalize_columns(snow)

    df_snow = pd.DataFrame({
        "Number": safe_get(snow, ["number", "incident"]),
        "Description": safe_get(snow, ["short description", "description"]),
        "Priority": safe_get(snow, ["priority"]),
        "Status": safe_get(snow, ["state"]),
        "Created By": safe_get(snow, ["opened by", "created by"]),
        "Created Date": safe_get(snow, ["opened", "created"]),
        "Assigned To": safe_get(snow, ["assigned to"]),
        "Resolved Date": safe_get(snow, ["resolved"]),
        "Source": "SNOW"
    })

    # ================= PTC =================
    ptc = pd.read_csv("data/Ptc.csv")
    ptc = normalize_columns(ptc)

    df_ptc = pd.DataFrame({
        "Number": safe_get(ptc, ["case number", "number"]),
        "Description": safe_get(ptc, ["subject", "description"]),
        "Priority": safe_get(ptc, ["severity", "priority"]),
        "Status": safe_get(ptc, ["status"]),
        "Created By": safe_get(ptc, ["contact", "created by"]),
        "Created Date": safe_get(ptc, ["created"]),
        "Assigned To": safe_get(ptc, ["assignee", "assigned to"]),
        "Resolved Date": safe_get(ptc, ["resolved"]),
        "Source": "PTC"
    })

    # ================= COMBINE =================
    df = pd.concat([df_azure, df_snow, df_ptc], ignore_index=True)

    # ================= CLEAN =================
    df = df.fillna("")

    return df, datetime.now().strftime("%d-%b-%Y %H:%M")
    
