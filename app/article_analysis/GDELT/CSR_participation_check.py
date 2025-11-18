#!/usr/bin/env python3
import pandas as pd
from collections import Counter, defaultdict

IDMAP_PATH    = "GDELT/theme_id_map.parquet"
ARTICLES_PATH = "GDELT/out_entities/articles/gkg_raw.parquet"
OUT_SUMMARY   = "GDELT/CSR_logging/missing_theme_codes_summary.csv"

def _parse_theme_codes(cell: str) -> list[str]:
    """Parse 'CODE,number;CODE,number;...' -> ['CODE','CODE', ...]"""
    if not isinstance(cell, str) or not cell.strip():
        return []
    out = []
    for it in cell.split(";"):
        it = it.strip()
        if not it:
            continue
        code = it.split(",", 1)[0].strip()
        if code:
            out.append(code)
    return out

def main():
    idmap = pd.read_parquet(IDMAP_PATH).rename(columns=str.lower)
    known = set(idmap["theme"])

    arts = pd.read_parquet(ARTICLES_PATH).rename(columns=str.lower)
    assert "themes" in arts.columns, f"Expected 'themes' column, got {arts.columns.tolist()}"
    # optional for examples
    url_col = "url" if "url" in arts.columns else None

    arts = arts.reset_index(drop=True)
    arts["codes"] = arts["themes"].apply(_parse_theme_codes)

    # coverage
    total_codes = arts["codes"].map(len).sum()
    matched = 0
    missing_counter = Counter()
    # store up to a few example rows/urls per missing code
    examples = defaultdict(list)

    for i, codes in enumerate(arts["codes"]):
        for c in codes:
            if c in known:
                matched += 1
            else:
                missing_counter[c] += 1
                if len(examples[c]) < 3:
                    examples[c].append(arts.iloc[i].get(url_col, f"row#{i}") if url_col else f"row#{i}")

    coverage = 0.0 if total_codes == 0 else matched / total_codes
    print(f"Coverage: {matched}/{total_codes} = {coverage:.1%}")
    print(f"Missing unique codes: {len(missing_counter)}")
    print("Top 25 missing codes:", missing_counter.most_common(25))

    # Suffix/base analysis to spot formatting patterns
    def split_base_suffix(code: str):
        parts = code.split("_")
        if len(parts) <= 1:
            return code, ""
        # base = everything except last token; suffix = last token
        return "_".join(parts[:-1]), parts[-1]

    rows = []
    for code, cnt in missing_counter.most_common():
        base, suffix = split_base_suffix(code)
        base_in_known = base in known
        rows.append({
            "code": code,
            "count": cnt,
            "base": base,
            "suffix": suffix,
            "base_in_known": base_in_known,
            "examples": " | ".join(examples[code]),
        })

    df_out = pd.DataFrame(rows)
    if not df_out.empty:
        # group info
        top_suffixes = (df_out.groupby("suffix")["count"].sum()
                        .sort_values(ascending=False).head(20))
        print("\nMost common suffixes among missing codes (top 20):")
        print(top_suffixes)

        print(f"\n→ Writing summary to {OUT_SUMMARY} (code, count, base, suffix, base_in_known, examples)")
        df_out.to_csv(OUT_SUMMARY, index=False)
    else:
        print("No missing codes 🎉")