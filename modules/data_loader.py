import pandas as pd
from datetime import datetime

def load_data():

    # -------- AZURE --------
    azure = pd.read_csv("data/Azure.csv")

    df_azure = pd.DataFrame({
        "Number": azure.get("ID"),
        "Description": azure.get("Title"),
        "Priority": azure.get("Release_windchill"),
        "Status": azure.get("State"),
        "Created By": azure.get("Created By"),
        "Created Date": azure.get("Created Date"),
        "Assigned To": azure.get("Assigned To"),
        "Resolved Date": azure.get("Resolved Date"),
        "Source": "AZURE"
    })

    # -------- SNOW --------
    snow = pd.read_excel("data/Snow.xlsx")

    df_snow = pd.DataFrame({
        "Number": snow.get("Number"),
        "Description": snow.get("Short Description"),
        "Priority": snow.get("Priority"),
        "Status": snow.get("Incident State"),
        "Created By": snow.get("Created"),
        "Created Date": snow.get("Date"),
        "Assigned To": snow.get("Assigned to"),
        "Resolved Date": snow.get("Resolved"),
        "Source": "SNOW"
    })

    # -------- PTC --------
    ptc = pd.read_csv("data/Ptc.csv")

    df_ptc = pd.DataFrame({
        "Number": ptc.get("CASE NUMBER"),
        "Description": ptc.get("SUBJECT"),
        "Priority": ptc.get("SEVERITY"),
        "Status": ptc.get("STATUS"),
        "Created By": ptc.get("CASE CONTACT"),
        "Created Date": ptc.get("CREATED DATE"),
        "Assigned To": ptc.get("CASE ASSIGNEE"),
        "Resolved Date": ptc.get("RESOLVED DATE"),
        "Source": "PTC"
    })

    df = pd.concat([df_azure, df_snow, df_ptc], ignore_index=True)

    return df, datetime.now().strftime("%d-%b-%Y %H:%M")
