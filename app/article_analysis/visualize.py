import pandas as pd
from tabulate import tabulate
# Mock sample rows (no BigQuery involved)
sample_data = [
    {
        "raw_date": 20251104190000,
        "source": "Reuters",
        "url": "https://www.reuters.com/markets/us-fed-signals-rate-cut-2025-11-04/",
        "themes": "ECON_INFLATION,120;ECON_STOCKMARKET,861;BANK,312",
    },
    {
        "raw_date": 20251104184522,
        "source": "Yahoo Finance",
        "url": "https://finance.yahoo.com/news/oil-prices-fall-global-demand-forecast",
        "themes": "ECON_COMMODITIES,542;ECON_OIL,443;ECON_GROWTH,321",
    },
    {
        "raw_date": 20251104183010,
        "source": "Bloomberg",
        "url": "https://www.bloomberg.com/news/articles/2025-11-04/fed-policy-outlook-drives-bond-yields-lower",
        "themes": "ECON_BONDS,710;ECON_INTEREST_RATES,905;ECON_FINSERV,267",
    },
    {
        "raw_date": 20251104180000,
        "source": "AP News",
        "url": "https://apnews.com/article/global-economy-outlook-2025",
        "themes": "ECONOMY,300;ECON_GDP,412;ECON_UNEMPLOYMENT,233",
    },
]

df = pd.DataFrame(sample_data)
print(tabulate(df, headers="keys", tablefmt="psql", showindex=False))
