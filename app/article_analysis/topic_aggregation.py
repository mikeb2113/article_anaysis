import requests
from bs4 import BeautifulSoup
import time
import random
import urllib.parse
proxies = [
    'http://customer-mikeb2113_G8Dql:Kalamazoocorgis3053@pr.oxylabs.io:7777',
    # Add more proxies if you have them
]

# List of user agents to rotate
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1'
]

def google_news_scraper(ticker, start_date, end_date, max_results=10):
    """
    Scrapes Google News for historical stock articles within a date range.
    """
    # Construct Google search URL with date filters
    search_url = f"https://www.google.com/search?q={ticker}+stock+forecast&tbs=cdr:1,cd_min:{start_date},cd_max:{end_date}&tbm=nws"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Send request
    response = requests.get(search_url, headers=headers)
    
    if response.status_code != 200:
        print("Failed to retrieve search results.")
        return []

    # Parse HTML content
    soup = BeautifulSoup(response.text, "html.parser")

    articles = []
    for result in soup.find_all("div", class_="BVG0Nb", limit=max_results):  # Finds news article blocks
        try:
            title = result.find("div", class_="mCBkyc").text
            link = result.find("a")["href"]
            source = result.find("div", class_="SVJrMe").text
            date = result.find("span", class_="WG9SHc").text

            articles.append({"title": title, "link": link, "source": source, "date": date})
        except AttributeError:
            continue  # Skip any incomplete results

    return articles

# Example Usage
ticker = "AAPL"
query = f"{ticker} stock forecast"
start_date = "01/01/2014"
end_date = "12/31/2014"

encoded_query = urllib.parse.quote(query)
search_url = f"https://www.google.com/search?q={encoded_query}&tbs=cdr:1,cd_min:{start_date},cd_max:{end_date}&tbm=nws"

print("Search URL:", search_url)