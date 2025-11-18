import pandas as pd
import marisa_trie

def main():
    df = pd.read_parquet("GDELT/theme_id_map.parquet")
    trie = marisa_trie.Trie(df["theme"].tolist())
    trie.save("GDELT/themes.trie")
    print("✅ saved trie")