from google.cloud import bigquery
from datetime import datetime, timedelta, timezone

PROJECT_ID = "article-analysis-001"
client = bigquery.Client(project=PROJECT_ID)

# Compute cutoff timestamp in GDELT INT format (YYYYMMDDHHMMSS)
cutoff_ts = int((datetime.now(timezone.utc) - timedelta(hours=2)).strftime("%Y%m%d%H%M%S"))

query = f"""
SELECT
  DATE AS raw_date,
  SourceCommonName AS source,
  DocumentIdentifier AS url,
  V2Themes AS themes
FROM `gdelt-bq.gdeltv2.gkg_partitioned`
WHERE _PARTITIONDATE = CURRENT_DATE()       -- only today's partition
  AND DATE >= @cutoff_ts                    -- hour-level filter
  AND REGEXP_CONTAINS(IFNULL(V2Themes, ''), r'(ECON|FINANC|BANK|STOCK)')
ORDER BY raw_date DESC
LIMIT 200
"""

params = [bigquery.ScalarQueryParameter("cutoff_ts", "INT64", cutoff_ts)]

dry = client.query(query, job_config=bigquery.QueryJobConfig(dry_run=True, query_parameters=params))
print("Estimated bytes (dry run):", dry.total_bytes_processed)

job = client.query(query, job_config=bigquery.QueryJobConfig(maximum_bytes_billed=500_000_000, query_parameters=params))
df = job.to_dataframe(create_bqstorage_client=True)

print(df)
print("Bytes processed:", job.total_bytes_processed)
print("Bytes billed:", job.total_bytes_billed)