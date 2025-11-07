#!/usr/bin/env python3
# pip install google-cloud-bigquery google-cloud-bigquery-storage pandas pyarrow db-dtypes tabulate

from google.cloud import bigquery
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tabulate import tabulate
import pandas as pd
import argparse
import re, unicodedata
import sys
import duckdb
from pathlib import Path
PROJECT_ID = "article-analysis-001"
OUT_DIR = Path("out_entities")
OUT_DIR.mkdir(exist_ok=True, parents=True)
DUCKDB_FILE = OUT_DIR / "gkg.duckdb"
SCHEMA = "gkg_schema"  # avoid name clash with any catalog named "gkg"
# ---------------- Helpers ----------------
def normalize_token(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^\w\s\-&]", "", s)
    return s.strip().lower()

def _sql_path(p: Path) -> str:
    return str(p).replace("'", "''")

def register_parquet_views(db_path: Path = DUCKDB_FILE):
    con = duckdb.connect(db_path.as_posix())

    # create schema in the main catalog
    con.execute(f'CREATE SCHEMA IF NOT EXISTS "{SCHEMA}"')
    
    paths = {
        "articles":  OUT_DIR / "articles"  / "gkg_raw.parquet",
        "persons":   OUT_DIR / "persons"   / "gkg_persons.parquet",
        "orgs":      OUT_DIR / "orgs"      / "gkg_orgs.parquet",
        "locations": OUT_DIR / "locations" / "gkg_locations.parquet",
    }

    for name, p in paths.items():
        if p.exists():
            sql = (
                f'CREATE OR REPLACE VIEW "{SCHEMA}".{name} AS '
                f"SELECT * FROM read_parquet('{_sql_path(p)}')"
            )
            try:
                con.execute(sql)
                print(f"✅ View {SCHEMA}.{name} -> {p}")
            except Exception as e:
                print(f"❌ Failed to create view {SCHEMA}.{name}: {e}")
        else:
            print(f"⏭️  Skipping {SCHEMA}.{name}: file not found -> {p}")

    return con

def parse_ts(raw_int) -> pd.Timestamp | None:
    try:
        s = str(int(raw_int))
        return pd.to_datetime(s, format="%Y%m%d%H%M%S", utc=True)
    except Exception:
        return None

def split_semicolon(cell: str) -> list[str]:
    if not isinstance(cell, str) or not cell.strip():
        return []
    return [x.strip() for x in cell.split(";") if x.strip()]

def parse_locations(cell: str) -> list[dict]:
    if not isinstance(cell, str) or not cell.strip():
        return []
    out = []
    for rec in cell.split(";"):
        rec = rec.strip()
        if not rec: continue
        parts = rec.split("#")
        parts += [""] * (8 - len(parts))
        typ, name, ccode, adm1, adm2, lat, lon, fid = parts[:8]
        try:
            latf = float(lat) if lat else None
            lonf = float(lon) if lon else None
        except ValueError:
            latf = lonf = None
        out.append({
            "loc_type": typ or None,
            "loc_name": name or None,
            "country_code": ccode or None,
            "adm1": adm1 or None,
            "adm2": adm2 or None,
            "lat": latf, "lon": lonf,
            "feature_id": fid or None,
        })
    return out

def pretty(df: pd.DataFrame, title: str, cols: list[str], limit: int = 25) -> None:
    if df.empty:
        print(f"\n=== {title} (no rows) ===")
        return
    view = df.copy()
    print(f"\n=== {title} (top {min(limit, len(view))}) ===")
    print(tabulate(view[cols].head(limit), headers="keys", tablefmt="psql",
                   showindex=False, stralign="left", disable_numparse=True))

def vc(df: pd.DataFrame, col: str) -> pd.DataFrame:
    if df.empty or col not in df.columns:
        return pd.DataFrame(columns=[col, "count"])
    return (
        df[col].value_counts()
        .reset_index(name="count")
        .rename(columns={"index": col})
    )

def partition_pred_for(hours_back: int) -> str:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=hours_back)
    if cutoff.date() == now.date():
        return "_PARTITIONDATE = CURRENT_DATE()"
    else:
        return "_PARTITIONDATE BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY) AND CURRENT_DATE()"

def build_query(mode: str, hours_back: int, finance_regex: str, include_locations_for_clean: bool) -> tuple[str, list]:
    # decide columns to select based on mode (minimize bytes scanned)
    base_cols = [
        "DATE AS raw_date",
        "SourceCommonName AS source",
        "DocumentIdentifier AS url",
        "V2Themes AS themes"
    ]
    if mode in ("persons", "all"):
        base_cols.append("V2Persons AS persons")
    if mode in ("orgs", "all"):
        base_cols.append("V2Organizations AS orgs")
    if mode in ("locations", "all"):
        base_cols.append("V2Locations AS locations")
    # If we need persons cleaning but mode=persons and include_locations_for_clean, we must fetch orgs/locations
    if mode == "persons" and include_locations_for_clean:
        if "V2Organizations AS orgs" not in base_cols:
            base_cols.append("V2Organizations AS orgs")
        if "V2Locations AS locations" not in base_cols:
            base_cols.append("V2Locations AS locations")

    select_clause = ",\n  ".join(base_cols)
    part_pred = partition_pred_for(hours_back)

    query = f"""
    SELECT
      {select_clause}
    FROM `gdelt-bq.gdeltv2.gkg_partitioned`
    WHERE
      {part_pred}
      AND DATE >= @cutoff_ts
      AND REGEXP_CONTAINS(IFNULL(V2Themes, ''), @finance_regex)
    ORDER BY raw_date DESC
    LIMIT 500
    """
    cutoff_ts = int((datetime.now(timezone.utc) - timedelta(hours=hours_back)).strftime("%Y%m%d%H%M%S"))
    params = [
        bigquery.ScalarQueryParameter("cutoff_ts", "INT64", cutoff_ts),
        bigquery.ScalarQueryParameter("finance_regex", "STRING", finance_regex),
    ]
    return query, params

def clean_persons_column_inplace(df: pd.DataFrame) -> int:
    """Remove person tokens that also appear as org or location names (if those cols exist)."""
    if "persons" not in df.columns:
        return 0
    have_orgs = "orgs" in df.columns
    have_locs = "locations" in df.columns

    def clean_row(row) -> str:
        ban = set()
        if have_orgs:
            ban |= {normalize_token(x) for x in split_semicolon(row.get("orgs", ""))}
        if have_locs:
            ban |= {
                normalize_token(loc.get("loc_name") or "")
                for loc in parse_locations(row.get("locations", ""))
                if loc.get("loc_name")
            }
        kept = []
        for p in split_semicolon(row.get("persons", "")):
            if normalize_token(p) in ban:
                continue
            kept.append(p)
        return ";".join(kept)

    before = df["persons"].fillna("").str.count(";").add(df["persons"].ne("").astype(int)).sum()
    df["persons"] = df.apply(clean_row, axis=1)
    after = df["persons"].fillna("").str.count(";").add(df["persons"].ne("").astype(int)).sum()
    return int(before - after)

def save_parquet(df: pd.DataFrame, path: Path):
    """
    Write a parquet file with good defaults for DuckDB.
    - zstd gives small files + fast reads
    - keep index off
    - pyarrow handles tz-aware timestamps
    """
    path.parent.mkdir(exist_ok=True, parents=True)
    df.to_parquet(path, engine="pyarrow", compression="zstd", index=False)

# ---------------- Main ----------------
def main():
    ap = argparse.ArgumentParser(description="GDELT GKG puller (finance-focused), mode-selective CSVs.")
    ap.add_argument(
        "--mode",
        choices=["articles", "persons", "orgs", "locations", "all"],
        help="Which output(s) to build."
    )
    ap.add_argument("--hours", type=int, default=2, help="Lookback window in hours (UTC).")
    ap.add_argument("--bytes-cap", type=int, default=1_200_000_000,
                    help="maximum_bytes_billed for BigQuery job.")
    ap.add_argument("--finance-regex", default="(ECON|FINANC|BANK|STOCK)",
                    help="Regex for V2Themes filter.")
    ap.add_argument("--clean-persons-overlaps", action="store_true",
                    help="If mode=persons or mode=all, remove persons that overlap org/location names (requires those cols to be selected).")
    args = ap.parse_args()

    if args.mode is None and sys.stdin.isatty():
        user_choice = input(
            "Please select a mode:\n1) articles | 2) persons | 3) orgs | 4) locations | 5) all (INTENSIVE! NOT SUGGESTED!) "
        ).strip().lower()
        mapping = {
            "1": "articles", "articles": "articles",
            "2": "persons",  "persons":  "persons",
            "3": "orgs",     "orgs":     "orgs",
            "4": "locations","locations":"locations",
            "5": "all",      "all":      "all",
        }
        args.mode = mapping.get(user_choice, "articles")
    else:
        args.mode = args.mode or "articles"
    print("resolved to " + args.mode)

    client = bigquery.Client(project=PROJECT_ID)
    query, params = build_query(
        mode=args.mode,
        hours_back=args.hours,
        finance_regex=args.finance_regex,
        include_locations_for_clean=args.clean_persons_overlaps
    )

    # Dry run to estimate bytes; bail if it'll exceed the cap.
    dry_cfg = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False, query_parameters=params)
    dry = client.query(query, job_config=dry_cfg)
    est = dry.total_bytes_processed
    print("Estimated bytes (dry run):", est)
    if est > args.bytes_cap:
        print(f"❌ Estimated bytes exceed cap ({est} > {args.bytes_cap}). "
              f"Try lowering --hours, changing --mode, or increasing --bytes-cap.")
        sys.exit(2)

    run_cfg = bigquery.QueryJobConfig(maximum_bytes_billed=args.bytes_cap, query_parameters=params)
    job = client.query(query, job_config=run_cfg)

    try:
        df = job.to_dataframe(create_bqstorage_client=True)
    except Exception as e:
        print("❌ Query failed:", e)
        sys.exit(1)

    print("Bytes processed:", job.total_bytes_processed)
    print("Bytes billed:", job.total_bytes_billed)

    if df.empty:
        print("\nNo rows in window; nothing to parse.")
        sys.exit(0)

    # Timestamp for downstream
    if "raw_date" in df.columns:
        df["ts"] = df["raw_date"].apply(parse_ts)

    # Clean persons overlaps if requested and possible
    removed = 0
    if args.clean_persons_overlaps and ("persons" in df.columns):
        removed = clean_persons_column_inplace(df)
        if removed:
            print(f"Removed {removed} person tokens that matched org/location names.")

    # Save per-mode outputs
    # 1) Articles (raw)
    if args.mode in ("articles", "all"):
        cols = [c for c in ["ts", "source", "url", "themes", "persons", "orgs", "locations"] if c in df.columns]
        save_parquet(df[cols], OUT_DIR / "articles" / "gkg_raw.parquet")
        pretty(df, "Articles", [c for c in ["ts","source","url"] if c in df.columns], limit=20)


    # 2) Persons
    if args.mode in ("persons", "all") and "persons" in df.columns:
        rows = []
        for _, r in df.iterrows():
            for p in split_semicolon(r.get("persons","")):
                rows.append({"ts": r.get("ts"), "source": r.get("source"), "url": r.get("url"), "person": p})
        persons = pd.DataFrame(rows, columns=["ts","source","url","person"]) if rows else pd.DataFrame(columns=["ts","source","url","person"])
        if not persons.empty:
            persons.drop_duplicates(["ts","url","person"], inplace=True)
            save_parquet(persons, OUT_DIR / "persons" / "gkg_persons.parquet")
            top_persons = vc(persons, "person")
            if not top_persons.empty:
                pretty(top_persons, "Top persons", ["person","count"])
        else:
            print("\n=== Persons (no data) ===")

    # 3) Orgs
    if args.mode in ("orgs", "all") and "orgs" in df.columns:
        rows = []
        for _, r in df.iterrows():
            for o in split_semicolon(r.get("orgs","")):
                rows.append({"ts": r.get("ts"), "source": r.get("source"), "url": r.get("url"), "org": o})
        orgs = pd.DataFrame(rows, columns=["ts","source","url","org"]) if rows else pd.DataFrame(columns=["ts","source","url","org"])
        if not orgs.empty:
            orgs.drop_duplicates(["ts","url","org"], inplace=True)
            save_parquet(orgs, OUT_DIR / "orgs" / "gkg_orgs.parquet")
            top_orgs = vc(orgs, "org")
            if not top_orgs.empty:
                pretty(top_orgs, "Top organizations", ["org","count"])
        else:
            print("\n=== Organizations (no data) ===")

    # 4) Locations
    if args.mode in ("locations", "all") and "locations" in df.columns:
        loc_rows = []
        for _, r in df.iterrows():
            for loc in parse_locations(r.get("locations","")):
                loc["ts"] = r.get("ts"); loc["source"] = r.get("source"); loc["url"] = r.get("url")
                loc_rows.append(loc)
        locs = pd.DataFrame(
            loc_rows,
            columns=["ts","source","url","loc_type","loc_name","country_code","adm1","adm2","lat","lon","feature_id"]
        ) if loc_rows else pd.DataFrame(columns=["ts","source","url","loc_type","loc_name","country_code","adm1","adm2","lat","lon","feature_id"])
        if not locs.empty:
            locs.drop_duplicates(["ts","url","loc_name","country_code"], inplace=True)
            save_parquet(locs, OUT_DIR / "locations" / "gkg_locations.parquet")
            top_locs = vc(locs, "loc_name")
            if not top_locs.empty:
                pretty(top_locs, "Top locations (by name)", ["loc_name","count"])
            locs_with_xy = locs.dropna(subset=["lat","lon"])
            if not locs_with_xy.empty:
                pretty(locs_with_xy, "Sample locations with coords",
                    ["ts","loc_name","country_code","lat","lon","url"], limit=20)
        else:
            print("\n=== Locations (no data) ===")

    # 5) Optional quick hits across entities (run only when we have respective frames)
    targets = ["nvidia","tsmc","amd","intel","semiconductor","gpu","copper","lme"]
    if args.mode in ("persons","all") and "persons" in df.columns:
        pass  # keep your custom hits section if desired, similar to your original
    con = register_parquet_views()
    print(con.execute(f'SELECT COUNT(*) AS n FROM "{SCHEMA}".articles').fetchdf())
    print(con.execute(f'''
    SELECT ts, source, url
    FROM "{SCHEMA}".articles
    ORDER BY ts DESC
    LIMIT 5
    ''').fetchdf())
    con.close()

if __name__ == "__main__":
    main()