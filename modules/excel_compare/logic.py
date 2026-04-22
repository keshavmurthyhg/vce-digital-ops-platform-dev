import pandas as pd


def compare_excels(old_file, new_file, key_column):

    old_df = pd.read_excel(old_file)
    new_df = pd.read_excel(new_file)

    old_df[key_column] = old_df[key_column].astype(str)
    new_df[key_column] = new_df[key_column].astype(str)

    # ---------- ADDED ----------
    added = new_df[~new_df[key_column].isin(old_df[key_column])]

    # ---------- REMOVED ----------
    removed = old_df[~old_df[key_column].isin(new_df[key_column])]

    # ---------- MODIFIED ----------
    common = pd.merge(
        old_df, new_df,
        on=key_column,
        how="inner",
        suffixes=("_old", "_new")
    )

    modified_rows = []

    for _, row in common.iterrows():
        changes = {}

        for col in old_df.columns:
            if col == key_column:
                continue

            old_val = row[f"{col}_old"]
            new_val = row[f"{col}_new"]

            if pd.isna(old_val) and pd.isna(new_val):
                continue

            if old_val != new_val:
                changes[col] = (old_val, new_val)

        if changes:
            modified_rows.append({
                key_column: row[key_column],
                "changes": changes
            })

    modified = pd.DataFrame(modified_rows)

    return old_df, new_df, added, removed, modified
