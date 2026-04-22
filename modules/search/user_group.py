import pandas as pd
import os

FILE_PATH = "data/user_group_mapping.csv"

DEFAULT_GROUP = "Unassigned"


def load_or_create_mapping(df):

    # Extract unique users
    users = pd.concat([
        df["Assigned To"],
        df["Created By"]
    ]).dropna().astype(str).unique()

    users_df = pd.DataFrame({"Name": sorted(users)})

    # If file exists → load
    if os.path.exists(FILE_PATH):
        mapping = pd.read_csv(FILE_PATH)
    else:
        mapping = pd.DataFrame(columns=["Name", "Group"])

    # Merge (preserve old order!)
    merged = mapping.merge(users_df, on="Name", how="outer", indicator=True)

    # Add new users at bottom
    new_users = merged[merged["_merge"] == "right_only"][["Name"]]
    new_users["Group"] = DEFAULT_GROUP

    final = pd.concat([
        mapping,
        new_users
    ], ignore_index=True)

    return final


def save_mapping(df):
    df.to_csv(FILE_PATH, index=False)
