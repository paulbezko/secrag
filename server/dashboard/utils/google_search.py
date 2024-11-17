from bs4 import BeautifulSoup
from googlesearch import search
import requests
import requests
import time

import tiktoken

token_encoder = tiktoken.encoding_for_model("gpt-4o-mini")

URL_BLACKLIST = [
    "finance.yahoo.com",
    "marketwatch.com"
]

firefox_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache'
}

def check_url_not_blacklisted(url):
    for blacklist_url in URL_BLACKLIST:
        if blacklist_url in url:
            return False
    return True

def get_html_text(url: str):
    '''Extracts text from web page'''
    retries = 0
    while retries < 2:
        response = requests.get(url, headers=firefox_headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()
            return text

        else:
            time.sleep(0.5)
            retries += 1
    return False

def search_with_retries(query: str, num_results: int = 10, max_retries: int = 3):
    retries = 0
    while retries < max_retries:
        try:
            results = search(query, num_results=10)
            for url in results:
                if check_url_not_blacklisted(url):
                    website_text = get_html_text(url)
                    if website_text:
                        return get_first_15000_tokens(website_text.strip())
            return "No parsable results found"
        except Exception as e:
            time.sleep(0.5)
            retries += 1

def get_first_15000_tokens(text):
    # Tokenize the input text
    tokens = token_encoder.encode(text)
    
    # Return the first 15,000 tokens, or the entire text if it's shorter
    return token_encoder.decode(tokens[:15000])

def google_search(query: str) -> str:
    '''Searches Google for links and return the first parsable link's text (Processes up to 10 links)'''
    return search_with_retries(query, num_results=10)
