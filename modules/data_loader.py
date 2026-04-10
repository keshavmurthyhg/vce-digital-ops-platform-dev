import pandas as pd
from datetime import datetime

def load_data():

    # ================= AZURE =================
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

    # ================= SNOW =================
    snow = pd.read_excel("data/Snow.xlsx")

    df_snow = pd.DataFrame({
        "Number": snow.get("Number"),
        "Description": snow.get("Short description"),  # ✅ FIXED
        "Priority": snow.get("Priority"),
        "Status": snow.get("State"),  # ✅ FIXED (not Incident State)
        "Created By": snow.get("Opened by"),  # ✅ FIXED
        "Created Date": snow.get("Opened"),   # ✅ FIXED
        "Assigned To": snow.get("Assigned to"),
        "Resolved Date": snow.get("Resolved"),
        "Source": "SNOW"
    })

    # ================= PTC =================
    ptc = pd.read_excel("data/Ptc.xlsx")  # ✅ USE XLSX (your actual file)

    df_ptc = pd.DataFrame({
        "Number": ptc.get("Case Number"),         # ✅ FIXED
        "Description": ptc.get("Subject"),        # ✅ FIXED
        "Priority": ptc.get("Severity"),          # ✅ FIXED
        "Status": ptc.get("Status"),              # ✅ FIXED
        "Created By": ptc.get("Contact"),         # ✅ FIXED
        "Created Date": ptc.get("Created"),       # ✅ FIXED
        "Assigned To": ptc.get("Assignee"),       # ✅ FIXED
        "Resolved Date": ptc.get("Resolved"),     # ✅ FIXED
        "Source": "PTC"
    })

    # ================= COMBINE =================
    df = pd.concat([df_azure, df_snow, df_ptc], ignore_index=True)

    # ================= CLEAN =================
    df = df.fillna("")

    return df, datetime.now().strftime("%d-%b-%Y %H:%M")
