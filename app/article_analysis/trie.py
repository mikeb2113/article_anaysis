import pandas as pd
import marisa_trie

def main():
    df = pd.read_parquet("theme_id_map.parquet")
    trie = marisa_trie.Trie(df["theme"].tolist())
    trie.save("themes.trie")
    print("✅ saved trie")