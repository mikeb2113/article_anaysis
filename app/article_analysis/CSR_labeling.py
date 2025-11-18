#!/usr/bin/env python3
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix, save_npz
from pathlib import Path

IDMAP_PATH   = Path("theme_id_map.parquet")     # from your cleaned theme table
ARTICLES_PATH= Path("out_entities/articles/gkg_raw.parquet")         # <- change to your file(s)
LABELS_OUT   = Path("labels.npz")
DOC_INDEX_OUT= Path("doc_index.parquet")        # to remember which doc is which row

def _parse_theme_codes(cell: str) -> list[str]:
    """Parse 'CODE,number;CODE,number;...' -> ['CODE','CODE', ...]"""
    if not isinstance(cell, str) or not cell.strip():
        return []
    items = [x.strip() for x in cell.split(";") if x.strip()]
    codes = []
    for it in items:
        # take substring before first comma (if any)
        code = it.split(",", 1)[0].strip()
        if code:
            codes.append(code)
    return codes

def main():
    # 1) load id map (source of truth)
    idmap = pd.read_parquet(IDMAP_PATH)
    idmap.columns = [c.strip().lower() for c in idmap.columns]
    labels = idmap.sort_values("theme_id")["theme"].tolist()
    theme_to_id = dict(zip(idmap["theme"], idmap["theme_id"]))
    L = len(labels)

    # 2) load articles
    arts = pd.read_parquet(ARTICLES_PATH)
    arts.columns = [c.strip().lower() for c in arts.columns]
    assert "themes" in arts.columns, f"Expected 'themes' column, got: {arts.columns.tolist()}"

    arts = arts.reset_index(drop=True)
    arts["doc_row"] = np.arange(len(arts), dtype=np.int64)

    # 3) parse + map to ids
    arts["theme_codes"] = arts["themes"].apply(_parse_theme_codes)
    def to_ids(codes):
        return sorted({ theme_to_id[c] for c in codes if c in theme_to_id })
    arts["theme_ids"] = arts["theme_codes"].apply(to_ids)

    # coverage stats (sanity check)
    total_codes = arts["theme_codes"].map(len).sum()
    mapped_codes = arts["theme_ids"].map(len).sum()
    coverage = 0.0 if total_codes == 0 else mapped_codes / total_codes
    print(f"Mapping coverage: {mapped_codes}/{total_codes} = {coverage:.1%}")

    # 4) keep labeled docs
    arts_keep = arts[arts["theme_ids"].map(len) > 0].reset_index(drop=True)
    N = len(arts_keep)

    # 5) build CSR
    indptr = [0]
    indices = []
    for lbls in arts_keep["theme_ids"]:
        indices.extend(lbls)
        indptr.append(len(indices))
    data = np.ones(len(indices), dtype=np.float32)
    Y = csr_matrix((data, np.array(indices, dtype=np.int32), np.array(indptr, dtype=np.int32)),
                   shape=(N, L))

    # 6) save
    save_npz(LABELS_OUT, Y)
    arts_keep[["doc_row"]].to_parquet(DOC_INDEX_OUT, index=False)

    print(f"✅ Saved CSR to {LABELS_OUT} → shape={Y.shape}, nnz={Y.nnz}")
    print(f"   Saved doc index to {DOC_INDEX_OUT} (rows kept: {N} of {len(arts)})")
    print("   Sample decoded labels for row 0 (if any):",
          [labels[i] for i in (Y[0].indices if N else [])][:10])