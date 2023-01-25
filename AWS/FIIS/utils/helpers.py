import numpy as np
import pandas as pd

def convert_string_to_float(df, colnames):
    for colname in colnames:
        df[colname] = df[colname].str.replace('[R$]', "", regex=True)
        df[colname] = df[colname].str.replace('.', "", regex=False)
        df[colname] = df[colname].str.replace(',', ".", regex=False)
        df[colname] = df[colname].apply(lambda x: float(x))
    return df


def convert_percentages_to_float(df, colnames):
    for colname in colnames:
            df[colname] = df[colname].str.replace('[R$]', "", regex=False)
            df[colname] = df[colname].str.replace('.', "", regex=False)
            df[colname] = df[colname].str.replace(',', ".", regex=False)
            df[colname] = df[colname].str.replace('%', "", regex=False)
            df[colname] = df[colname].apply(lambda x: float(x))
            df[colname] = (df[colname] / 100).round(4)

    return df


def convert_to_datetime(x):
    try:
        x = pd.to_datetime(x, format = "%d/%m/%Y")
    except ValueError:
        x = np.nan
    return x