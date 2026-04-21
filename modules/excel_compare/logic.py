import pandas as pd


def compare_excels(file1, file2):
    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)

    # Align both dataframes (important if shapes differ)
    df1, df2 = df1.align(df2, join='outer', axis=None)

    return df1, df2


def highlight_differences(df1, df2):
    def highlight(row):
        result = []
        for col_index in range(len(row)):
            val1 = row.iloc[col_index]
            val2 = df2.iloc[row.name, col_index] if row.name < len(df2) else None

            if pd.isna(val1) and pd.isna(val2):
                result.append('')
            elif val1 != val2:
                result.append('background-color: yellow')
            else:
                result.append('')
        return result

    return df1.style.apply(highlight, axis=1)


def generate_output(df1, df2, output_path="comparison_output.xlsx"):
    styled_df = highlight_differences(df1, df2)

    # Save styled Excel
    styled_df.to_excel(output_path, engine='openpyxl')

    return output_path
