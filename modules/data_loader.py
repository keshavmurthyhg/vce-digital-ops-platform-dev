import pandas as pd

# -------------------------------
# NORMALIZE
# -------------------------------
def norm(df):
    df.columns = df.columns.astype(str).str.strip().str.lower()
    return df

# -------------------------------
# SAFE COLUMN FETCH
# -------------------------------
def col(df, *names):
    for n in names:
        if n in df.columns:
            return df[n]
    return None

# -------------------------------
# AZURE
# -------------------------------
def build_azure(df):
    return pd.DataFrame({
        "Number": col(df, "id"),
        "Description": col(df, "title"),
        "Priority": None,
        "Status": col(df, "state"),
        "Created By": col(df, "created by"),
        "Created Date": col(df, "created date"),
        "Assigned To": col(df, "assigned to"),
        "Resolved Date": col(df, "resolved date"),
        "Release": col(df, "release_windchill"),
        "Source": "AZURE"
    })

# -------------------------------
# SNOW
# -------------------------------
def build_snow(df):
    return pd.DataFrame({
        "Number": col(df, "number"),
        "Description": col(df, "short description"),
        "Priority": col(df, "priority"),
        "Status": col(df, "incident state"),
        "Created By": col(df, "opened by", "created by"),
        "Created Date": col(df, "created", "date"),
        "Assigned To": col(df, "assigned to"),
        "Resolved Date": col(df, "resolved"),
        "Release": None,
        "Source": "SNOW"
    })

# -------------------------------
# PTC (FIXED BASED ON YOUR IMAGE)
# -------------------------------
def build_ptc(df):
    return pd.DataFrame({
        "Number": col(df, "case number"),
        "Description": col(df, "subject"),
        "Priority": col(df, "severity"),
        "Status": col(df, "status"),
        "Created By": col(df, "case contact"),
        "Created Date": col(df, "created date"),
        "Assigned To": col(df, "case assignee"),
        "Resolved Date": col(df, "resolved date"),
        "Release": col(df, "release name"),
        "Source": "PTC"
    })

# -------------------------------
# LOAD DATA
# -------------------------------
def load_data():

    azure = pd.read_csv(
        "https://raw.githubusercontent.com/keshavmurthyhg/vce-digital-ops-platform-dev/main/data/Azure.csv"
    )

    snow = pd.read_excel(
        "https://raw.githubusercontent.com/keshavmurthyhg/vce-digital-ops-platform-dev/main/data/Snow.xlsx",
        engine="openpyxl"
    )
ptc = pd.read_csv(
    "https://raw.githubusercontent.com/keshavmurthyhg/vce-digital-ops-platform-dev/main/data/Ptc.csv",
    sep=";",           # try comma first
    engine="python",
    encoding="utf-8",
    on_bad_lines="skip"
)

    # normalize
    azure = norm(azure)
    snow = norm(snow)
    ptc = norm(ptc)

    # build unified data
    df = pd.concat([
        build_azure(azure),
        build_snow(snow),
        build_ptc(ptc)
    ], ignore_index=True)

    return df, {
        "AZURE": "Updated",
        "SNOW": "Updated",
        "PTC": "Updated"
    }
