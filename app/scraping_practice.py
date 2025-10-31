import random
import undetected_chromedriver as uc
import time
import pickle
import requests
from selenium.webdriver.common.by import By

# ✅ List of User-Agents (Rotates randomly)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]

# ✅ Free Proxy Function
def get_free_proxy():
    try:
        response = requests.get("https://www.sslproxies.org/")
        proxy_list = response.text.split("\n")
        return random.choice(proxy_list)  # Pick a random proxy
    except:
        return None  # If free proxies fail, continue without a proxy

# ✅ Human-like scrolling function
def human_scroll(driver):
    scroll_amounts = [300, 500, 700, 900]
    for _ in range(random.randint(3, 6)):  # Scroll multiple times
        driver.execute_script(f"window.scrollBy(0, {random.choice(scroll_amounts)});")
        time.sleep(random.uniform(1, 3))

# ✅ Store and load cookies (Makes Google think you’re a returning user)
def load_cookies(driver):
    try:
        driver.get("https://www.google.com/")
        with open("cookies.pkl", "rb") as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
    except FileNotFoundError:
        print("[INFO] No cookies found, starting fresh session.")

def save_cookies(driver):
    pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))

# ✅ Main function with full anti-detection measures
def scrape_google_with_selenium(ticker, start_date, end_date):
    """
    Uses Selenium to scrape Google search results while avoiding bot detection.
    """
    search_url = f"https://www.google.com/search?q={ticker}+stock+forecast&tbs=cdr:1,cd_min:{start_date},cd_max:{end_date}"
    print(f"[INFO] Search URL: {search_url}")

    # ✅ Choose a random User-Agent
    user_agent = random.choice(USER_AGENTS)

    # ✅ Use free proxy (if available)
    proxy = get_free_proxy()

    options = uc.ChromeOptions()
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent bot detection
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    options.add_argument("--headless=new")  # ✅ Fixes headless mode

    # ✅ Use proxy if available
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")

    # ✅ Launch Chrome (UC automatically makes it undetectable)
    driver = uc.Chrome(version_main=131,options=options, patcher_force_close=True)

    # ✅ Run JavaScript to Hide Automation Flags
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    # ✅ Load cookies if available
    load_cookies(driver)

    try:
        print("[INFO] Loading page...")
        driver.get(search_url)
        time.sleep(random.uniform(3, 7))  # Randomized delay

        # ✅ CAPTCHA Handling
        if "detected unusual traffic" in driver.page_source.lower():
            print("[ERROR] Google has blocked the request with CAPTCHA.")
            input("[ACTION REQUIRED] Solve the CAPTCHA manually and press Enter to continue...")
            driver.get(search_url)  # Retry after solving CAPTCHA

        print("[INFO] Scrolling to simulate human behavior...")
        human_scroll(driver)

        search_results = driver.find_elements(By.CSS_SELECTOR, "a")
        print(f"[INFO] Found {len(search_results)} anchor tags.")

        links = []
        for link in search_results:
            href = link.get_attribute("href")
            if href and "/url?q=" in href:
                clean_link = href.split("/url?q=")[1].split("&")[0]
                links.append(clean_link)

        # ✅ Save cookies for next session
        save_cookies(driver)

        driver.quit()
        print(f"[INFO] Extracted {len(links)} valid links.")
        return links

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        driver.quit()
        return []

# ✅ Example usage
ticker = "AAPL"
start_date = "01/01/2014"
end_date = "12/31/2014"

results = scrape_google_with_selenium(ticker, start_date, end_date)

if results:
    print("\n[INFO] Final Results:")
    for idx, link in enumerate(results):
        print(f"{idx+1}. {link}")
else:
    print("[ERROR] No links were extracted.")
#Right now, code will make a google search for the given stock, assuming the given start and end dates
#You need to take the HTML contents and extract any <link> attributes. Access these URLs and perform analysis from here
#Anti-bot measures will need to be taken. Selenium, proxy, etc. Consider the robots.txt file
#The lack of output implies some sort of bot throttling. Account for this, get results in test file, then implement to sentiment_analysis.py
#Once this is done, there isn't much more until the project is completed. Keep going!