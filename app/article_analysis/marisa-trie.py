import marisa_trie
import pandas as pd

df = pd.read_parquet("theme_list.parquet")
trie = marisa_trie.Trie(df["THEME"].tolist())
trie.save("themes.trie")