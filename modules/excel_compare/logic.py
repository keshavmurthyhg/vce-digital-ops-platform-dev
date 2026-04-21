import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
import tempfile


def compare_excels(file1, file2):
    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)

    # Align both dataframes
    df1, df2 = df1.align(df2, join='outer', axis=None)

    return df1, df2


def get_diff_mask(df1, df2):
    return df1.ne(df2)


def style_dataframe(df, diff_mask):
    def highlight(row):
        return [
            'background-color: yellow' if diff_mask.iloc[row.name, i] else ''
            for i in range(len(row))
        ]
    return df.style.apply(highlight, axis=1)


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
            val1 = ws1.cell(r, c).value
            val2 = ws2.cell(r, c).value

            if val1 != val2:
                ws1.cell(r, c).fill = fill
                ws2.cell(r, c).fill = fill

    # Save outputs
    temp1 = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    temp2 = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")

    wb1.save(temp1.name)
    wb2.save(temp2.name)

    return temp1.name, temp2.name
