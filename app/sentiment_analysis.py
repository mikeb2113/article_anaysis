import os
import pandas as pd
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
import feedparser
from datetime import datetime, timedelta
import time
import random
import urllib.request
import concurrent.futures
import json
import os
from bs4 import BeautifulSoup
import requests
from newspaper import Article
from collections import Counter
import re
import logging
from selenium import webdriver
import time
from selenium import webdriver
from ratelimit import limits, sleep_and_retry
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from requests.exceptions import RequestException, ConnectionError
from collections import defaultdict
import string

#Cramer observed that when a large number of investors align on one side of a trade, as seen currently, that group often ends up being incorrect.

class Node:
    def __init__(self, value=None):
        self.value = value
        self.left = None
        self.right = None

def generate_ngrams(text: str, n: int) -> list[str]:
    if isinstance(text, str):  # Check that text is a string
        words = [word.lower() for word in text.split()]
    else:
        raise TypeError("Expected a string for `text`, but got a list.")
    # Remove punctuation and split text into words
    words = [''.join(char for char in word if char not in string.punctuation) for word in text.lower().split()]
    if n == 1:
        return words  # Return individual words for unigrams
    else:
        return [' '.join(words[i:i + n]) for i in range(len(words) - n + 1)]
def generate_offset_ngrams(text: str, n: int) -> list[str]:
    if isinstance(text, str):  # Check that text is a string
        words = [word.lower() for word in text.split()]
        standard_ngrams = [' '.join(words[i:i + n]) for i in range(len(words) - n + 1)]
        offset_ngrams = [' '.join(words[i+1:i + n + 1]) for i in range(len(words) - n)]
        return standard_ngrams + offset_ngrams
    else:
        raise TypeError("Expected a string for `text`, but got a list.")

class QuadTree:
    def __init__(self, original_text, n):
        self.nodes = []
        self.index = {}  # Dictionary to store nodes by value for quick lookup
        self.build_QuadTree(original_text, n)

    def build_QuadTree(self, original_text, n):
        ngrams = generate_ngrams(original_text, n)
        
        # Create nodes for each n-gram and link them sequentially
        prev = None
        for ngram in ngrams:
            curr = Node(ngram)
            self.nodes.append(curr)
            
            # Link nodes in text order
            if prev:
                prev.right = curr
                curr.left = prev
            prev = curr
            
            # Add to index for search, handling duplicates by storing a list
            if ngram in self.index:
                self.index[ngram].append(curr)
            else:
                self.index[ngram] = [curr]

    def search_ngram(self, ngram, context_words=2):
        # Check if the ngram exists
        if ngram in self.index:
            for node in self.index[ngram]:
                # Gather flexible context around the node
                context = self._get_context(node, context_words)
                # Debug logging to understand context filtering
                print(f"Checking context for n-gram '{ngram}' in article: '{context}'")
                
                # Flexible match: Check if ngram appears within a close context match
                if self._is_flexible_match(context, ngram):
                    return True, context
        return False, None

    def _is_flexible_match(self, context, ngram):
        # Consider context a match if it includes the n-gram and maintains core meaning
        ngram_words = set(ngram.split())
        context_words = set(context.split())
        
        # Allow slight variations but ensure essential words are present
        return ngram_words.issubset(context_words)

    def _get_context(self, node, context_words):
        # Collect context by traversing left and right from the node
        context = [node.value]
        
        left_node = node.left
        left_context = []
        for _ in range(context_words):
            if left_node:
                left_context.insert(0, left_node.value)
                left_node = left_node.left
            else:
                break
        
        right_node = node.right
        right_context = []
        for _ in range(context_words):
            if right_node:
                right_context.append(right_node.value)
                right_node = right_node.right
            else:
                break

        full_context = ' '.join(left_context + context + right_context)
        return full_context

    def print_QuadTree(self):
        # Print the linked nodes in sequential order for verification
        node = self.nodes[0] if self.nodes else None
        while node:
            left_val = node.left.value if node.left else None
            right_val = node.right.value if node.right else None
            print(f"Node: {node.value}, Left: {left_val}, Right: {right_val}")
            node = node.right


def compare_phrases_with_sample(url: str, positive_example_text: str, sample_text: str, n: int):
    sample_QuadTree = QuadTree(sample_text, n)
    matches = []  # To collect all matches with detailed information

    for line in positive_example_text.splitlines():
        phrase = line.strip()
        positive_ngrams = generate_offset_ngrams(phrase, n)  # Generate standard and offset n-grams

        match_count = 0
        for ngram in positive_ngrams:
            match_found, context = sample_QuadTree.search_ngram(ngram)
            if match_found and sample_QuadTree._is_flexible_match(context, ngram):  # Use flexible context check
                print(f"Exact match found for n-gram '{ngram}' in sample text for URL: {url}")
                matches.append((url, phrase, ngram))  # Track detailed match data
                match_count += 1
            else:
                print(f"False positive filtered for n-gram '{ngram}' due to partial context match in URL: {url}")

        if match_count == 0:
            print(f"No match found for phrase: '{phrase}' in URL: {url}")
        else:
            print(f"{match_count} exact matches found for phrase: '{phrase}' in URL: {url}")

    return matches  # Return all matched n-grams with detailed information

def initialize_comparison_map(website_list, emolex_dict, window_size=6):
    """Creates an initial hashmap with all possible website comparisons and initializes weight to 0."""
    comparison_map = {}

    # Convert websites into Link objects
    link_objects = {site: Link(window_size, is_string=True, adjacent_words=site) for site in website_list}

    for i, link_one in enumerate(website_list):
        for j, link_two in enumerate(website_list):
            if i >= j:
                continue  # Avoid redundant comparisons

            if link_one not in comparison_map:
                comparison_map[link_one] = {}

            if link_two not in comparison_map[link_one]:
                comparison_map[link_one][link_two] = {}

            for word in emolex_dict:
                comparison_map[link_one][link_two][word] = 0  # Initialize weight to 0

    return comparison_map, link_objects


def process_article_comparisons(website_list, emolex_dict, window_size=6):
    """Processes articles iteratively using Link objects and an odd/even stack for comparisons."""
    
    # Initialize data structures
    comparison_map, link_objects = initialize_comparison_map(website_list, emolex_dict, window_size)

    odd_links_stack = list(link_objects.values())  # Convert Link objects to stack
    even_links_stack = []

    while odd_links_stack:
        current_link = odd_links_stack.pop(0)  # Pop first link from odds
        even_links_stack.append(current_link)

        for existing_link in even_links_stack:
            if existing_link.website == current_link.website:
                continue  # Skip self-comparison

            # Ensure both comparison directions exist
            if existing_link.website not in comparison_map:
                comparison_map[existing_link.website] = {}

            if current_link.website not in comparison_map[existing_link.website]:
                comparison_map[existing_link.website][current_link.website] = {}

            # Compare words in their respective windows
            for word in emolex_dict:
                window_one = set(existing_link.window_check(word))
                window_two = set(current_link.window_check(word))

                if window_one and window_two:
                    comparison_map[existing_link.website][current_link.website][word] += 1  # Increment weight

    return comparison_map



def load_emolex_dict(file_path='NRC-Emotion-Lexicon-Wordlevel-v0.92.txt'):
    emolex_df = pd.read_csv(file_path, sep='\t', header=None, names=['word', 'emotion', 'association'])
    # Keep the word as it is, even if it's a phrase, then group by it
    emolex_dict = emolex_df.groupby('word')['emotion'].apply(list).to_dict()
    return emolex_dict

def extract_links_from_rss(rss_string):
    if rss_string is None:
        print("RSS string is None, cannot parse.")
        return []

    # Parse the RSS feed
    feed = feedparser.parse(rss_string)

    # Extract links from the feed entries
    links = []
    for entry in feed.entries:
        if 'link' in entry:
            links.append(entry.link)
        else:
            print("No link found")

    #print("Extracted Links:", links)
    return links

@limits(calls=10, period=60)
def parse_url(url, user_agents, proxies):
    now = datetime.now()

    # Check if the URL is in the cache and if it's still valid
    if url in cache and (now - cache[url]['timestamp']) < cache_duration:
        print(f"Using cached data for URL: {url}")
        return cache[url]['data']

    headers = {'User-Agent': random.choice(user_agents)}
    proxy = random.choice(proxies) if proxies else None

    try:
        time.sleep(1)  # 1-second delay between requests
        response = requests.get(url, headers=headers, proxies={'http': proxy, 'https': proxy} if proxy else None)
        response.raise_for_status()

        # Process the HTML to clean and extract main content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Use common HTML tags for main article body extraction
        # Many articles are contained within <article>, <main>, or <div> with specific classes
        main_content = soup.find('article') or soup.find('main')
        if not main_content:
            main_content = soup.find('div', class_="main-content")  # Adjust this class based on common article sites

        if main_content:
            # Remove any unwanted tags within the main content (e.g., ads, scripts, sidebars)
            for tag in main_content(['script', 'style', 'aside', 'footer']):
                tag.decompose()  # Removes the tag and its contents

            # Get cleaned text
            data = main_content.get_text(separator="\n", strip=True)
        else:
            data = "Main article body could not be identified."

        # Cache the cleaned data
        cache[url] = {'timestamp': now, 'data': data}
        # Save the updated cache to file
        save_cache_to_file(cache)

        print(f"Fetched and cleaned data from URL: {url}")
        print(f"Contents of the article body: {data[:500]}...")  # Print first 500 characters for brevity

        return data
    except requests.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code} - {e.response.reason}")
    except requests.RequestException as e:
        print(f"Request Error: {e}")
    except Exception as e:
        print(f"General Error: {str(e)}")
    return None

#def filter_text(text, emolex_dict):
    # Initialize an empty list to store the found emotional words/phrases
    filtered_words = []
    text_lower = text.lower()
    #This stores the text in lower_case letters. This would be a good spot to insert the hash solution
    print("text_lower = " + text_lower)
    # Iterate through the keys (words/phrases) in the emolex dictionary
    for word in emolex_dict.keys():
        word_lower = word.lower()
        start = 0
        while start < len(text_lower):
            start = text_lower.find(word_lower, start)
            if start == -1:
                break
            # Check if the found word is a whole word
            if (start == 0 or not text_lower[start - 1].isalnum()) and (start + len(word_lower) == len(text_lower) or not text_lower[start + len(word_lower)].isalnum()):
                #print(f"Matched word: {word}")
                filtered_words.append(word)
            start += len(word_lower)
        #else:
            #print(f"No match found for word: {word_lower}")

    return filtered_words

def filter_text(text, emolex_dict):
    print("Input Text:", text)
    
    # Create the word map from the text using the quadtree
    quadtree = create_word_map_from_text(text)
    
    # Check if the quadtree is empty
    if not quadtree or not quadtree.root:
        print("The word map is empty.")
        return []
    
    # Traverse through each word in the quadtree (left-right traversal)
    current_node = quadtree.root
    matched_words = []
    
    while current_node:
        word = current_node.value
        
        # Check if the word is in emolex_dict for sentiment analysis
        if word in emolex_dict:
            matched_words.append(word)
            # Optional: print associated emotions
            emotions = emolex_dict[word]
            print(f"Matched Word: {word}, Emotions: {', '.join(emotions)}")
        
        # Move to the next node in the right sequence
        current_node = current_node.right
    
    return matched_words

#def categorize_emotions(emolex_dict, sorted_list):
    positive_emotions = {'joy', 'trust', 'anticipation', 'surprise', 'positive'}
    negative_emotions = {'anger', 'disgust', 'fear', 'sadness', 'negative'}
    
    emotion_score = 0
    for word in sorted_list:
        if word in emolex_dict:
            for emotion in emolex_dict[word]:
                if emotion in positive_emotions:
                    emotion_score += 1
                elif emotion in negative_emotions:
                    emotion_score -= 1
    return emotion_score

def categorize_emotions(emolex_dict, sorted_list):
    positive_emotions = {'joy', 'trust', 'anticipation', 'surprise', 'positive'}
    negative_emotions = {'anger', 'disgust', 'fear', 'sadness', 'negative'}
    
    emotion_score = 0
    
    for linked_list in sorted_list:
        # Traverse each DoublyLinkedList object
        current_node = linked_list.head  # Assuming DoublyLinkedList has a head pointer
        while current_node is not None:
            word = current_node.value
            if word in emolex_dict:
                for emotion in emolex_dict[word]:
                    if emotion in positive_emotions:
                        emotion_score += 1
                    elif emotion in negative_emotions:
                        emotion_score -= 1
            current_node = current_node.next  # Move to the next node in the list
    
    return emotion_score

def clean_cache(cache, cache_duration):
    now = datetime.now()
    # Identify cache entries that are older than the cache duration
    keys_to_remove = [url for url, data in cache.items() if now - data['timestamp'] > cache_duration]
    # Remove the outdated cache entries
    for key in keys_to_remove:
        del cache[key]

def get_sentiment_category(score):
    if score <= -5:
        return "Very Negative"
    elif -4 <= score <= -1:
        return "Negative"
    elif 0 <= score <= 5:
        return "Neutral"
    elif 6 <= score <= 50:
        return "Positive"
    elif score >= 51:
        return "Very Positive"

# Retry strategy for specific network-related and Chrome errors
@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=30), retry=retry_if_exception_type(ConnectionError))
def analyze_website(url, positive_example_text, user_agents, proxies, n=3, attempt=1):
    driver = None
    try:
        # Setup Selenium Chrome options
        options = webdriver.ChromeOptions()
        options.page_load_strategy = 'none'
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-extensions')
        options.add_argument('--remote-debugging-port=0')

        # Initialize the WebDriver
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(60)
        driver.set_script_timeout(60)

        logging.info(f"Fetching URL with Selenium: {url}")
        
        # Fetch the website content
        driver.get(url)

        # Handle cookie consent pop-ups
        try:
            accept_button = driver.find_element_by_xpath("//button[text()='Accept']")
            accept_button.click()
            time.sleep(2)
        except Exception as e:
            logging.info(f"No cookie consent button found or clicked: {e}")

        # Close other types of pop-ups (e.g., Close or Cancel)
        for button_text in ['Close', 'Cancel']:
            try:
                button = driver.find_element_by_xpath(f"//button[text()='{button_text}']")
                button.click()
                time.sleep(2)
            except Exception as e:
                logging.info(f"No {button_text} button found or clicked: {e}")

        # Wait for the page to fully render
        time.sleep(5)

        # Extract page source and quit the driver
        page_source = driver.page_source
        driver.quit()

        # Parse the page content with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Extract meaningful text content
        potential_tags = ['article', 'div', 'section', 'p']
        text = ''
        for tag in potential_tags:
            elements = soup.find_all(tag)
            for element in elements:
                if 'cookie' in element.get('class', []) or 'advertisement' in element.get('class', []):
                    continue
                text += ' '.join([p.get_text() for p in element.find_all('p')])

            if text.strip():  # Stop if meaningful content is found
                break

        if not text.strip():
            logging.warning(f"No significant text content found for URL: {url}")
            print(f"Attempt {attempt}: No significant content found for {url}.")
            return [], 0

        logging.info(f"Extracted Text from {url}:\n{text[:500]}...")  # Preview the first 500 characters
        print(f"Attempt {attempt}: Successfully extracted content from {url}.")

        # Match n-grams with the positive examples from the file content, pass URL for logging
        matches = compare_phrases_with_sample(url, positive_example_text, text, n)
        match_count = len(matches)

        return matches, match_count

    except ConnectionError as e:
        logging.error(f"Network connection error while analyzing {url}: {e}")
        print(f"Attempt {attempt}: Connection error while accessing {url}. Retrying...")
        if driver is not None:
            driver.quit()
        raise e

    except Exception as e:
        if "disconnected: not connected to DevTools" in str(e):
            logging.error(f"Chrome DevTools disconnection error for URL: {url}")
            print(f"Attempt {attempt}: DevTools disconnection error for {url}. Retrying...")
            if driver is not None:
                driver.quit()
            raise e
        else:
            logging.error(f"General error while analyzing {url}: {e}")
            print(f"Attempt {attempt}: General error while accessing {url}. Retrying...")
            if driver is not None:
                driver.quit()
            raise e

    finally:
        if driver is not None:
            driver.quit()
            logging.info(f"WebDriver closed for URL: {url}")


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=30), retry=retry_if_exception_type(Exception))
def process_url(url, emolex_dict, user_agents, proxies):
    try:
        emotion_score, sentimental_words = analyze_website(url, emolex_dict, user_agents, proxies)
        print(f"Successfully processed {url}. Emotion score: {emotion_score}")
        return emotion_score, sentimental_words #GOAL: return a list of words
    except Exception as e:
        logging.error(f"Failed to process {url} after retries: {e}")
        print(f"Giving up on {url} after multiple failed attempts.")
        return 0, []

    
def analyze_website_with_selenium(url):
    logging.info(f"Starting analysis for URL: {url}")
    
    try:
        # Initialize the Selenium WebDriver with headless option
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        driver = webdriver.Chrome(options=options)

        logging.info(f"WebDriver initialized. Fetching URL: {url}")
        
        # Open the webpage
        driver.get(url)
        logging.info(f"Page loaded: {url}")
        
        # Wait for JavaScript to execute
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))        
        # Extract the page source (rendered HTML)
        text = driver.page_source
        logging.info(f"Page source extracted. Length: {len(text)} characters")

        # Use BeautifulSoup to parse the content
        soup = BeautifulSoup(text, 'html.parser')
        paragraphs = soup.find_all('p')
        article_text = ' '.join([p.get_text() for p in paragraphs])

        if not article_text.strip():
            logging.warning(f"No significant text content found for URL: {url}")
        else:
            logging.info(f"Extracted Text from {url}:\n{article_text[:500]}...")  # Log the first 500 characters

        return article_text

    except Exception as e:
        logging.error(f"Error during Selenium processing for URL: {url}. Error: {e}")
        return ""
    finally:
        driver.quit()
        logging.info(f"WebDriver closed for URL: {url}")

def save_cache_to_file(cache, file_path='cache.json'):
    # Prepare the cache data for saving
    cache_to_save = {url: {'timestamp': cache[url]['timestamp'].strftime('%Y-%m-%d %H:%M:%S.%f'), 'data': cache[url]['data']} for url in cache}
    # Save the cache to a file
    with open(file_path, 'w') as file:
        json.dump(cache_to_save, file)

def load_cache_from_file(file_path='cache.json'):
    if os.path.exists(file_path):
        # Load the cache from the file
        with open(file_path, 'r') as file:
            cache = json.load(file)
            # Convert the timestamp strings back to datetime objects
            for url in cache:
                cache[url]['timestamp'] = datetime.strptime(cache[url]['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
            return cache
    print(f"No cache file found at {file_path}, creating a new one.")
    return {}

def find_top_words(word_counter, top_percent=10):
    total_words = sum(word_counter.values())
    
    # Calculate the percent abundance for each word, ignoring "fool"
    word_abundance = {word: (count / total_words) * 100 for word, count in word_counter.items() if word.lower() != 'fool'}
    
    # Sort the words by their percent abundance in descending order
    sorted_words = sorted(word_abundance.items(), key=lambda item: item[1], reverse=True)
    
    # Determine the top 20% most occurring words
    top_count = max(1, int(len(sorted_words) * top_percent))
    top_words = [word for word, _ in sorted_words[:top_count]]
    
    return top_words

#Later adjust this function: only adjust the sentiment value if a word is found within a coherent context. (AKA: is a word has a non-empty Context list)
#The score should be adjusted in such a way that is weighted to both words, such that if one word changes the emphesis of the sentence then the overall 
#emotional conclusion of that sentence will be recorded. Weighted average? The longer the context of a word and the better the match, the more weight.
#Also consider removing words and phrases that are contained withing quotes, so that if someone else's words arae being used in a critical context they 
#won't be considered - only the analysis of said words.
def analyze_links(links, positive_example_file, user_agents, proxies, n=3):
    avg_match_count = 0
    total_matches = Counter()  # Track n-gram matches across all links
    url_results = {}  # Dictionary to store results for each URL

    # Read the contents of the positive example phrases from the file
    with open(positive_example_file, 'r') as f:
        positive_example_text = f.read()

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(analyze_website, link, positive_example_text, user_agents, proxies, n): link for link in links}
        
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            print(f"Accessing link: {url}")
            try:
                matches, match_count = future.result()  # Detailed match results from analyze_website

                # Store detailed results for the URL
                url_results[url] = {
                    "match_count": match_count,
                    "matches": matches
                }

                # Update counters
                avg_match_count += match_count
                total_matches.update([ngram for _, _, ngram in matches])
                print(f"Successfully processed {url} with {match_count} n-gram matches found.")
            except Exception as e:
                print(f"Error processing {url}: {e}")

    # Calculate the average match count per link
    avg_match_count = avg_match_count / len(links) if links else 0
    print(f"Average Match Count: {avg_match_count}")

    # Find the top 20% most frequently matched n-grams
    top_matched_ngrams = find_top_words(total_matches, top_percent=0.20)

    # Display structured results for each URL
    print("\nDetailed Results by URL:")
    for url, results in url_results.items():
        print(f"URL: {url}")
        print(f"Match Count: {results['match_count']}")
        print("Matched Details:")
        for _, phrase, ngram in results['matches']:
            print(f"  Phrase: '{phrase}', N-gram: '{ngram}'")

    return avg_match_count, top_matched_ngrams
    #Output looks like: (4.0, [('stock market crash', 15), ('AI predictions', 12), ('market trends', 9)]) 4.0 being the average match count, the other numbers being the occurances of n-grams

#Error processing https://news.google.com/rss/articles/CBMirwFBVV95cUxQZkhyWUhUa0ZQUFpyaVVRRmgxYTZMZVZMeV85c0dMbjBIa1pkcTlyV2xEaEhMUHdEYjEzbFQteVYwTXBxcnIxbkQydHpEZGVYc2w2THFGNk10MlcxcVVVd1kwLW9WM0pWQ2pFTzRKbXJZRWN5alVyeXg2azFqdGlfSUpoVHFsa3FEUmJubW1jSTZ6cFlDYUNTZ2JmVkp5LTY0UU8xMkJ5WTB5TkRfZzJ3?oc=5: expected str, bytes or os.PathLike object, not dict
#Note: it seems like this is not allowed to progress since the link is being treated as a n-gram. Change this so that it handles the link first, then turns it to an n-gram data type later.

#Error processing https://news.google.com/rss/articles/CBMigAFBVV95cUxPRmVUelc4QTI2LWQ4THJhQXZuLWdac1RzaTU1cE5oTFFhci13ZFRNUHoteENlOXY2MDF2Q1VUVnk2Y21vdC15QldwQ0p6UHkzNzItVENqZlRQTVNoSnQ1NTZFekZNNHZwYVU5bGRfSF9US092bnhQTThIRHRxaWNESdIBhgFBVV95cUxObjR0Q3dhdDlOM3J1cnlBbHgxME9nV1JYV3BFYzg3SEZJVGh5R0VUdHBzdC03bUxjRFFIN1lGbW1PMEZfcnM3ZGd6Mm50RXBRZVZUUkhSSVVkQ1ZMdmRVUktDaW5mR1BCa2tlMmt3UnFRQk1tWU1PYndfanowQmczUlAtNTZjdw?oc=5: can only concatenate str (not "NoneType") to str

#ERROR:root:General error while analyzing https://news.google.com/rss/articles/CBMiswFBVV95cUxNU3B2bVc1dXlNLU43Y2NrSWJSZHdRb3BOR3UyQlVKNkFMWTV2ZEc4MzBzM09GZ2RqRVNkZm1CMDNBdHZVckxROXVUVVRsMWdLRThLY3ZNYmMxMHB5VjcyWHdGUmoxNGhtODJSX0c1VzdEUHNxTnhiMlV3OXFFaHNLNE9wMkUzcU9aeTJ0N1preUtoZ1VPZWpZdkJNRWVvUEFlMndYNkttN1JWOU96Y1N6TkZ0NNIBuAFBVV95cUxPWHAtdGxoTTNKb0pNRjJVOVFVMl80VVlvaHpXOXJVZ3kzdXc0MW9NSlpRcThielF6ZkhoYk10ck0xTlFYVklzdVZjOF9LTnhVTjFVdHNubjZkdWxJZlgxd2FXN29BSkIxS3ZvTGFBRU9scTdYR1V5X1R4cXRhRVNFRmtQb2xWTFBTUUZFU2JNelBhdlZLZ2ZLQVhlZVpDMDNEZmV5eFhrXzJPU2xCWkZEQ0tBVDJocDdn?oc=5: expected str, bytes or os.PathLike object, not dict

def find_common_words(words_list, min_occurrences=2):
    counter = Counter(words_list)
    common_words = [word for word, count in counter.items() if count >= min_occurrences]
    return common_words



def create_word_map_from_text(text):
    # Split text into segments outside of quotes
    outside_quotes_segments = re.split(r'["“”]', text)
    cleaned_words = []

    # Process only segments outside quotes
    for idx, segment in enumerate(outside_quotes_segments):
        if idx % 2 == 1:
            continue  # Skip segments inside quotes
        # Extract words outside of quotes
        words = re.findall(r'\b\w+\b', segment.lower())
        cleaned_words.extend(words)
    
    # Create and populate the quadtree with the cleaned words
    quadtree = QuadTree()
    quadtree.build_from_words(cleaned_words)
    
    return quadtree

def print_word_map(dancing_links_list):
    # Check if the dancing links list is empty
    if dancing_links_list.head is None:
        print("The word map is empty.")
        return
    
    # Start at the head of the list
    current_node = dancing_links_list.head
    printed_words = set()  # Track printed words to avoid duplicates in the circular list
    
    while current_node and current_node.value not in printed_words:
        printed_words.add(current_node.value)
        
        # Print the current word
        print(f"Word: {current_node.value}")
        
        # Collect context words
        context_words = []
        
        # Get the previous word
        prev_node = current_node.left if current_node.left != dancing_links_list.head else None
        if prev_node:
            context_words.append(f"Previous: {prev_node.value}")
        else:
            context_words.append("Previous: None")
        
        # Get the next word
        next_node = current_node.right if current_node.right != dancing_links_list.head else None
        if next_node:
            context_words.append(f"Next: {next_node.value}")
        else:
            context_words.append("Next: None")
        
        # Print context
        print("  Context:", " | ".join(context_words))
        
        # Move to the next node
        current_node = current_node.right

#def create_word_map(file_path):
    # Change defaultdict to hold lists of DoublyLinkedList objects
    #word_map = defaultdict(list)
    
    #with open(file_path, 'r') as file:
        #for line in file:
            #cleaned_words = re.findall(r'\b\w+\b', line.lower())
            
            #for i in range(len(cleaned_words)):
                #key = cleaned_words[i]
                #linked_list = DoublyLinkedList()
                #for word in cleaned_words[i+1:]:
                    #linked_list.append(word)
                
                # Append the linked list to the list of contexts for the key
                #word_map[key].append(linked_list)

    #return word_map


# Build the map based on the 'positive_example.txt' document
#positive_word_map = create_word_map('positive_example.txt')
#print("Positive Example Word Map:")
# Print each key with its list of linked lists of following words
#for key, linked_lists in positive_word_map.items():
#    print(f"Key: '{key}' -> Values:")
#    for i, linked_list in enumerate(linked_lists, 1):
#        print(f"  Context {i}: {linked_list.to_list()}")

# Build the map based on the 'negative_example.txt' document
#negative_word_map = create_word_map('negative_example.txt')
#print("\nNegative Example Word Map:")
#for key, linked_list in negative_word_map.items():
#    print(f"Key: '{key}' -> Value:", linked_list.to_list())

# Initialize cache
# List of user agents to rotate
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1'
]

# List of proxies to rotate (replace with actual proxies)
proxies = [
    'http://customer-mikeb2113_G8Dql:Kalamazoocorgis3053@pr.oxylabs.io:7777',
    # Add more proxies if you have them
]

def main():
    cache_duration = timedelta(hours=1)
    cache = load_cache_from_file()
    emolex_dict = load_emolex_dict()
    # Use selection to determine the nature of our stock search. This approach is really, really good for recent stock trends. 
    # However, this won't find any articles older than a month.
    ticker = input("Input stock ticker: ")
    days = input("Input how many days you'd like to go back: ")
    time = 1
    rss_feed_url = ""
    if time == 1:
        rss_feed_url = f"https://news.google.com/rss/search?q={ticker}+stock+when:{days}d&hl=en-US&gl=US&ceid=US:en"
    print(rss_feed_url)
    rss_feed_content = rss_feed_url  # parse_url(rss_feed_url, user_agents, proxies)
    links = extract_links_from_rss(rss_feed_content)

    # Call analyze_links with positive example text instead of emolex_dict
    avg_match_count_pos, top_matched_ngrams_pos = analyze_links(links, "positive_example.txt", user_agents, proxies)
    avg_match_count_neg, top_matched_ngrams_neg = analyze_links(links, "negative_example.txt", user_agents, proxies)

    print("The average match count with positive phrases is: " + str(avg_match_count_pos))
    print("Top matched n-grams: " + ", ".join(top_matched_ngrams_pos))
    print("The average match count with positive phrases is: " + str(avg_match_count_neg))
    print("Top matched n-grams: " + ", ".join(top_matched_ngrams_neg))
    

main()
# Example usage

# Convert the text to a single line
# Build the QuadTree for bigrams (n=2)
#quad_map = QuadTree(single_line_text, n)
#quad_map.print_QuadTree()

# Search for a specific bigram
#search_phrase = "last year"
#found_nodes = quad_map.search_ngram(search_phrase)
#if found_nodes:
#    for node in found_nodes:
#        print(f"Found n-gram: {node.value}")
#else:
#    print("N-gram not found")



#single_line_text = sample_text.replace("\n", " ")
#n = 3
#compare_phrases_with_sample("positive_example.txt", single_line_text, n)


#actionable plan:
#1) create the emolex_dict object. this will be used to ping words to use as keys in the positive and negative example maps
#2) Consider using a different data structure/approach for the emotional words
#It would be useful to have some sort of way to save a word and create connotation maps for them
#Maybe use the same function used to create the positive and negative maps on the articles themselves, and compare them map for map?
#Note that this may be taxing on the resources of the computer... Look into this later.