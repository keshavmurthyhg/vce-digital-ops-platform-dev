import pandas as pd
from config import CONFIG, ENV


def load_data():

    config = CONFIG[ENV]
    all_data = []

    for key, url in config.items():

        try:
            # --- LOAD FILE ---
            if url.endswith(".csv"):
                df = pd.read_csv(url)
            else:
                df = pd.read_excel(url)

            # --- SOURCE NAME ---
            source_name = key.replace("_URL", "")
            df["Source"] = source_name

            # --- PTC COLUMN MAPPING (ONLY STRUCTURE, NOT RESOLUTION) ---
            if source_name == "PTC":
                df.rename(columns={
                    "Case Number": "Number",
                    "Summary": "Description",
                    "Created On": "Created Date",
                    "Owner": "Assigned To"
                }, inplace=True)

            # --- GLOBAL STANDARDIZATION ---
            # 👉 Convert ALL possible variants → "Resolved Date"
            df.rename(columns={
                "Resolution Date": "Resolved Date",
                "Resolved On": "Resolved Date",
                "Closed Date": "Resolved Date"
            }, inplace=True)

            # --- ENSURE REQUIRED COLUMNS EXIST ---
            required_cols = [
                "Number",
                "Description",
                "Priority",
                "Status",
                "Created By",
                "Created Date",
                "Assigned To",
                "Resolved Date"
            ]

            for col in required_cols:
                if col not in df.columns:
                    df[col] = None

            # --- KEEP ONLY RELEVANT COLUMNS ---
            df = df[required_cols + ["Source"]]

            all_data.append(df)

        except Exception as e:
            print(f"❌ Error loading {key}: {e}")

    # --- FINAL MERGE ---
    if not all_data:
        return pd.DataFrame(), {}

    final_df = pd.concat(all_data, ignore_index=True)

    return final_df, {"last_refresh": "Auto"}
