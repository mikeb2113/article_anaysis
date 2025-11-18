import pandas as pd

def main():
    df = pd.read_parquet("theme_list.parquet")

    # normalize column names
    df.columns = [c.lower() for c in df.columns]

    # keep only the theme column
    df = df[["theme"]].drop_duplicates().reset_index(drop=True)

    # assign stable int IDs
    df["theme_id"] = range(len(df))

    df.to_parquet("theme_id_map.parquet", index=False)

    print(df.head())
    print("total themes:", len(df))