import pandas as pd
from datetime import datetime

def read_file(path):
    try:
        return pd.read_csv(path)
    except:
        return pd.DataFrame()


def build_azure(df):
    if df.empty:
        return df

    return pd.DataFrame({
        "Number": df.get("ID"),
        "Description": df.get("Title"),
        "Priority": df.get("Release_windchill"),
        "Status": df.get("State"),
        "Created By": df.get("Created By"),
        "Created Date": df.get("Created Date"),
        "Assigned To": df.get("Assigned To"),
        "Resolved Date": df.get("Resolved Date"),
        "Source": "AZURE"
    })


def build_snow(df):
    if df.empty:
        return df

    return pd.DataFrame({
        "Number": df.get("Number"),
        "Description": df.get("Short Description"),
        "Priority": df.get("Priority"),
        "Status": df.get("Incident State"),
        "Created By": df.get("Created"),
        "Created Date": df.get("Date"),
        "Assigned To": df.get("Assigned to"),
        "Resolved Date": df.get("Resolved"),
        "Source": "SNOW"
    })


def build_ptc(df):
    if df.empty:
        return df

    return pd.DataFrame({
        "Number": df.get("CASE NUMBER"),
        "Description": df.get("SUBJECT"),
        "Priority": df.get("SEVERITY"),
        "Status": df.get("STATUS"),
        "Created By": df.get("CASE CONTACT"),
        "Created Date": df.get("CREATED DATE"),
        "Assigned To": df.get("CASE ASSIGNEE"),
        "Resolved Date": df.get("RESOLVED DATE"),
        "Source": "PTC"
    })


def load_data():
    azure = read_file("data/Azure.csv")
    snow = read_file("data/Snow.csv")
    ptc = read_file("data/Ptc.csv")

    df_azure = build_azure(azure)
    df_snow = build_snow(snow)
    df_ptc = build_ptc(ptc)

    df = pd.concat([df_azure, df_snow, df_ptc], ignore_index=True)

    df = df.fillna("")

    info = {
        "AZURE": datetime.now().strftime("%d-%b-%Y %H:%M"),
        "SNOW": datetime.now().strftime("%d-%b-%Y %H:%M"),
        "PTC": datetime.now().strftime("%d-%b-%Y %H:%M")
    }

    return df, info
