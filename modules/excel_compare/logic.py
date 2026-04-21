import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
import tempfile
import zipfile
import os
from datetime import datetime


SECTION_HEADERS = [
    "New Parts",
    "Revised Parts",
    "New Documents",
    "Revised Documents",
    "Non Production / Obsolete / RG4 Parts",
    "Structure Changes",
    "Line Number Changes",
    "Associated sBOMs",
    "Serial No. / Effectivity"
]


def normalize(val):
    if pd.isna(val):
        return ""
    return str(val).strip()


# =========================
# LOAD DATA
# =========================
def compare_excels(file1, file2):
    df1 = pd.read_excel(file1, header=None)
    df2 = pd.read_excel(file2, header=None)

    return df1, df2


# =========================
# SECTION DETECTION
# =========================
def extract_sections(df):
    sections = {}
    current_section = None

    for idx, row in df.iterrows():
        first_val = normalize(row.iloc[0])

        if first_val in SECTION_HEADERS:
            current_section = first_val
            sections[current_section] = []

        elif current_section:
            sections[current_section].append(idx)

    return sections


# =========================
# EXTRACT NUMBERS
# =========================
def extract_numbers(df, rows):
    numbers = set()

    for idx in rows:
        val = normalize(df.iloc[idx, 0])
        if val and val != "Number":
            numbers.add(val)

    return numbers


# =========================
# SECTION BASED DIFF
# =========================
def section_diff_logic(df1, df2):
    sections1 = extract_sections(df1)
    sections2 = extract_sections(df2)

    diff_mask = pd.DataFrame(False, index=df1.index, columns=df1.columns)

    summary = {}
    total_diff = 0

    for section in SECTION_HEADERS:
        rows1 = sections1.get(section, [])
        rows2 = sections2.get(section, [])

        set1 = extract_numbers(df1, rows1)
        set2 = extract_numbers(df2, rows2)

        added = set2 - set1
        removed = set1 - set2

        summary[section] = {
            "added": len(added),
            "removed": len(removed)
        }

        total_diff += len(added) + len(removed)

        # highlight removed in file1
        for idx in rows1:
            val = normalize(df1.iloc[idx, 0])
            if val in removed:
                diff_mask.iloc[idx, :] = True

    return diff_mask, summary, total_diff


# =========================
# STYLE
# =========================
def style_dataframe(df, diff_mask):
    def highlight(row):
        return [
            "background-color: yellow" if diff_mask.iloc[row.name, i] else ""
            for i in range(len(row))
        ]

    return df.style.apply(highlight, axis=1)


# =========================
# EXCEL OUTPUT
# =========================
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

            if is_empty(v1) and is_empty(v2):
                continue

            if normalize(v1) != normalize(v2):
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

    # ===== ZIP =====
    date_str = datetime.now().strftime("%d%b%Y")
    zip_name = f"Excel-Compare_{date_str}.zip"
    zip_path = os.path.join(temp_dir, zip_name)

    with zipfile.ZipFile(zip_path, "w") as z:
        z.write(path1, name1)
        z.write(path2, name2)

    return zip_path, zip_name
