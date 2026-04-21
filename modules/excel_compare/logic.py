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
    col_summary = diff_mask.sum().to_dict()

    total_diff = int(sum(col_summary.values()))

    return {
        "total_diff": total_diff,
        "column_wise": col_summary
    }


# =========================
# GENERATE OUTPUT (KEEP FORMAT)
# =========================
import zipfile
from datetime import datetime
import os


def is_empty(val):
    return val is None or str(val).strip() == ""


def generate_output(file1, file2):
    wb1 = load_workbook(file1)
    wb2 = load_workbook(file2)

    ws1 = wb1.active
    ws2 = wb2.active

    fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")

    max_row = min(ws1.max_row, ws2.max_row)
    max_col = min(ws1.max_column, ws2.max_column)

    for r in range(1, max_row + 1):
        for c in range(1, max_col + 1):
            v1 = ws1.cell(r, c).value
            v2 = ws2.cell(r, c).value

            # 🔥 IGNORE BOTH EMPTY
            if is_empty(v1) and is_empty(v2):
                continue

            if str(v1).strip() != str(v2).strip():
                ws1.cell(r, c).fill = fill
                ws2.cell(r, c).fill = fill

    # ===== FILE NAMES =====
    name1 = os.path.splitext(file1.name)[0] + "_Highlighted.xlsx"
    name2 = os.path.splitext(file2.name)[0] + "_Highlighted.xlsx"

    temp_dir = tempfile.mkdtemp()

    path1 = os.path.join(temp_dir, name1)
    path2 = os.path.join(temp_dir, name2)

    wb1.save(path1)
    wb2.save(path2)

    # ===== ZIP CREATION =====
    date_str = datetime.now().strftime("%d%b%Y")
    zip_name = f"Excel-Compare_{date_str}.zip"
    zip_path = os.path.join(temp_dir, zip_name)

    with zipfile.ZipFile(zip_path, 'w') as z:
        z.write(path1, name1)
        z.write(path2, name2)

    return zip_path, zip_name

    return temp1.name, temp2.name
