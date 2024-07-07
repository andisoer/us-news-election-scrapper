import json
import os

from gnews import GNews
from newspaper import Article, ArticleException
from datetime import datetime

# Define function to check if item is exist inside a list
def item_exist(news_item, news_list):
    return any(existing_item['title'] == news_item['title'] for existing_item in news_list)

# Define function to merge existing news and recently fetched news
def merge_news(news_list, existing_news_list): 
    for news in news_list:
        if not item_exist(news, existing_news_list):
            existing_news_list.append(news)
    return existing_news_list

# Config GNews
google_news = GNews()
google_news.country = 'United States'
google_news.language = 'English'
google_news.start_date = (2024, 1, 1)
google_news.max_results = 20

# Fetch news using GNews
us_news = google_news.get_news('United State Election')

# Mapping image_url from newspaper to gnews result
for news in us_news:
    article = Article(news['url'])
    try:
        article.download()
        article.parse()
        news['image_url'] = article.top_image
    except ArticleException:
        print('failed to download from', news['url'])
        continue

# Read from existing us_news.json
us_news_json_file = 'us_news.json'
if os.path.exists(us_news_json_file):
    with open(us_news_json_file) as file:
        existing_us_news = json.load(file)

# Call the merge news function
merged_us_news = merge_news(us_news, existing_us_news)

sorted_merged_us_news = sorted(merged_us_news, key=lambda x:datetime.strptime(x['published date'], '%a, %d %b %Y %H:%M:%S %Z'), reverse=True)

# Convert the merged news to us_news.json
us_news_json = json.dumps(sorted_merged_us_news, indent=4)

# Write to json
with open(us_news_json_file, "w") as outfile:
    outfile.write(us_news_json)

