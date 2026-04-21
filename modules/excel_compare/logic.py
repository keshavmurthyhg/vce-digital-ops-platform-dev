import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
import tempfile


# =========================
# CLEAN VALUES
# =========================
def normalize(val):
    if pd.isna(val):
        return ""
    return str(val).strip()


# =========================
# COMPARE USING KEY COLUMN
# =========================
def compare_excels(file1, file2, key_column="Number"):
    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)

    if key_column in df1.columns and key_column in df2.columns:
        df1 = df1.set_index(key_column)
        df2 = df2.set_index(key_column)

    # Align based on key
    df1, df2 = df1.align(df2, join="outer", axis=0)

    return df1, df2


# =========================
# DIFF MASK (IGNORE BLANKS)
# =========================
def get_diff_mask(df1, df2):
    mask = pd.DataFrame(False, index=df1.index, columns=df1.columns)

    for col in df1.columns:
        for idx in df1.index:
            v1 = normalize(df1.at[idx, col]) if idx in df1.index else ""
            v2 = normalize(df2.at[idx, col]) if idx in df2.index else ""

            if v1 != v2:
                mask.at[idx, col] = True

    return mask


# =========================
# STYLE DATAFRAME
# =========================
def style_dataframe(df, diff_mask):
    def highlight(row):
        return [
            "background-color: yellow" if diff_mask.iloc[row.name, i] else ""
            for i in range(len(row))
        ]

    return df.style.apply(highlight, axis=1)


# =========================
# SUMMARY
# =========================
def get_summary(diff_mask):
    total_cells = diff_mask.size
    diff_cells = diff_mask.sum().sum()

    changed_rows = diff_mask.any(axis=1).sum()
    changed_cols = diff_mask.any(axis=0).sum()

    return {
        "total_cells": total_cells,
        "diff_cells": int(diff_cells),
        "changed_rows": int(changed_rows),
        "changed_cols": int(changed_cols),
    }


# =========================
# GENERATE OUTPUT (KEEP FORMAT)
# =========================
def generate_output(file1, file2):
    wb1 = load_workbook(file1)
    wb2 = load_workbook(file2)

    ws1 = wb1.active
    ws2 = wb2.active

    fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")

    max_row = max(ws1.max_row, ws2.max_row)
    max_col = max(ws1.max_column, ws2.max_column)

    for r in range(1, max_row + 1):
        for c in range(1, max_col + 1):
            v1 = ws1.cell(r, c).value
            v2 = ws2.cell(r, c).value

            if normalize(v1) != normalize(v2):
                ws1.cell(r, c).fill = fill
                ws2.cell(r, c).fill = fill

    temp1 = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    temp2 = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")

    wb1.save(temp1.name)
    wb2.save(temp2.name)

    return temp1.name, temp2.name
