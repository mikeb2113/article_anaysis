import pandas as pd

df = pd.read_parquet("out_entities/articles/gkg_raw.parquet")
print(df.shape)         # number of rows, columns
print(df.columns)       # column names
print(df.head())        # first 5 rows

df = pd.read_parquet("theme_id_map.parquet")
print(df.shape)         # number of rows, columns
print(df.columns)       # column names
print(df.head())        # first 5 rows