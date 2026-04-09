import pandas as pd
from datetime import datetime

# ------------------ COMMON CLEAN ------------------
def clean_name(val):
    if pd.isna(val):
        return ""
    return str(val).split("<")[0].strip()


# ------------------ AZURE ------------------
def build_azure(df):
    if df.empty:
        return df

    return pd.DataFrame({
        "Number": df.get("ID"),
        "Description": df.get("Title"),
        "Priority": df.get("Release_windchill"),
        "Status": df.get("State"),
        "Created By": df.get("Created By").apply(clean_name),
        "Created Date": df.get("Created Date"),
        "Assigned To": df.get("Assigned To").apply(clean_name),
        "Resolved Date": df.get("Resolved Date"),
        "Link": "",
        "Source": "AZURE"
    })


# ------------------ SNOW (FIXED XLSX ISSUE) ------------------
def build_snow(df):
    if df.empty:
        return df

    return pd.DataFrame({
        "Number": df.get("Number"),
        "Description": df.get("Short Description"),
        "Priority": df.get("Priority"),
        "Status": df.get("Incident State"),
        "Created By": df.get("Created").apply(clean_name),
        "Created Date": df.get("Date"),
        "Assigned To": df.get("Assigned to").apply(clean_name),
        "Resolved Date": df.get("Resolved"),
        "Link": "",
        "Source": "SNOW"
    })


# ------------------ PTC (STRICT MATCH) ------------------
def build_ptc(df):
    if df.empty:
        return df

    df.columns = df.columns.str.strip().str.upper()

    return pd.DataFrame({
        "Number": df.get("CASE NUMBER"),
        "Description": df.get("SUBJECT"),
        "Priority": df.get("SEVERITY"),
        "Status": df.get("STATUS"),
        "Created By": df.get("CASE CONTACT").apply(clean_name),
        "Created Date": df.get("CREATED DATE"),
        "Assigned To": df.get("CASE ASSIGNEE").apply(clean_name),
        "Resolved Date": df.get("RESOLVED DATE"),
        "Link": "https://support.ptc.com/appserver/cs/view/case.jsp?n=" + df.get("CASE NUMBER").astype(str),
        "Source": "PTC"
    })


# ------------------ LOAD ------------------
def load_data():
    try:
        azure = pd.read_csv("data/Azure.csv")
    except:
        azure = pd.DataFrame()

    try:
        snow = pd.read_excel("data/Snow.xlsx")   # IMPORTANT FIX
    except:
        snow = pd.DataFrame()

    try:
        ptc = pd.read_csv("data/Ptc.csv")
    except:
        ptc = pd.DataFrame()

    df = pd.concat([
        build_azure(azure),
        build_snow(snow),
        build_ptc(ptc)
    ], ignore_index=True)

    df = df.fillna("")

    info = datetime.now().strftime("%d-%b-%Y %H:%M")

    return df, info
