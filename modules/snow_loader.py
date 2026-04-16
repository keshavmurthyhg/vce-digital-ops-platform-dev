import pandas as pd

def load_snow_data():
    df = pd.read_excel("data/snow.xlsx")

    # normalize columns
    df.columns = df.columns.str.strip().str.lower()

    return df
