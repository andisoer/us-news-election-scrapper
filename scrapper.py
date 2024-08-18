import json
import os
import re
import base64

from gnews import GNews
from newspaper import Article, ArticleException
from datetime import datetime
from urllib.parse import urlparse
from splinter import Browser
from time import sleep

# Define function to check if item is exist inside a list
def item_exist(news_item, news_list):
    return any(existing_item['title'] == news_item['title'] for existing_item in news_list)

# Define function to merge existing news and recently fetched news
def merge_news(news_list, existing_news_list): 
    for news in news_list:
        if not item_exist(news, existing_news_list):
            existing_news_list.append(news)
    return existing_news_list

# Function to convert date format
def format_published_date(date_str):
    # Parse the date string into a datetime object
    date_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
    # Format the datetime object to desired format
    return date_obj.strftime('%d %B %Y')
    
def scrap_news(query, file_name):
    # Fetch news using GNews
    us_news = google_news.get_news(query)

    # Mapping image_url from newspaper to gnews result
    for news in us_news:
        browser = Browser("firefox")
        browser.visit(news["url"])
        
        sleep(5)
        url = browser.url

        browser.quit()

        # real_url = decode_google_news_url(news['url'])
        article = Article(url)
        try:
            article.download()
            article.parse()
            news['image_url'] = article.top_image
            news['authors'] = article.authors
            news['real_url'] = url
        except ArticleException:
            print('failed to download from', news['url'])
            continue

    # Change the published date key name to published_date
    for news in us_news:
        news['published_date'] = news.pop('published date')

    # Read from existing file name
    if os.path.exists(file_name):
        with open(file_name) as file:
            existing_us_news = json.load(file)

    # Convert the recently fetched news date format 
    for news in us_news:
        news['published_date'] = format_published_date(news['published_date'])

    # Call the merge news function if existing news exist
    if os.path.exists(file_name):
        merged_us_news = merge_news(us_news, existing_us_news)
    else:
        merged_us_news = us_news

        
    # Sort by date decrement (newest date)
    sorted_merged_us_news = sorted(merged_us_news, key=lambda x:datetime.strptime(x['published_date'], '%d %B %Y'), reverse=True)

    # Change the date format from published_date key
    # for news in sorted_merged_us_news:
    #     news['published_date'] = format_published_date(news['published_date'])

    # Convert the merged news to us_news.json
    us_news_json = json.dumps(sorted_merged_us_news, indent=4)

    # Write to json
    with open(file_name, "w") as outfile:
        outfile.write(us_news_json)

# Config GNews
google_news = GNews()
google_news.country = 'United States'
google_news.language = 'English'
google_news.start_date = (2024, 1, 1)
google_news.max_results = 20


election_candidate_file = 'election_candidate.json'
if os.path.exists(election_candidate_file):
    with open(election_candidate_file) as file:
        election_candidates = json.load(file)

        for candidate in election_candidates:
            print("====== Fetching ", candidate['query'], " ======")
            scrap_news(candidate["query"], candidate["file_name"])
