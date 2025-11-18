import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

def main():
    theme_csv = 'GDELT THEMES LIST.csv'
    df = pd.read_csv(theme_csv)
    df["THEME"] = df["THEME"].astype("category")
    table = pa.Table.from_pandas(df,preserve_index=False)
    parquet_output = "./theme_list.parquet"
    pq.write_table(table,parquet_output,compression="zstd",compression_level=7)