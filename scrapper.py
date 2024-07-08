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

# Function to convert date format
def format_published_date(date_str):
    # Parse the date string into a datetime object
    date_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
    # Format the datetime object to desired format
    return date_obj.strftime('%d %B %Y')

# Config GNews
google_news = GNews()
google_news.country = 'United States'
google_news.language = 'English'
google_news.start_date = (2024, 1, 1)
google_news.max_results = 20

# Query:
# United State Election, Joe Biden, Donald Trump
news_query = "Joe Biden"

# Fetch news using GNews
us_news = google_news.get_news(news_query)

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

# Change the published date key name to published_date
for news in us_news:
    news['published_date'] = news.pop('published date')

# Read from existing file name
# File name
# 'us_news.json', 'joe_biden_news.json', 'donald_trump.json'
us_news_json_file = 'joe_biden_news.json'
if os.path.exists(us_news_json_file):
    with open(us_news_json_file) as file:
        existing_us_news = json.load(file)

# Convert the recently fetched news date format 
for news in us_news:
    news['published_date'] = format_published_date(news['published_date'])

# Call the merge news function
merged_us_news = merge_news(us_news, existing_us_news)
    
# Sort by date decrement (newest date)
sorted_merged_us_news = sorted(merged_us_news, key=lambda x:datetime.strptime(x['published_date'], '%d %B %Y'), reverse=True)

# Change the date format from published_date key
# for news in sorted_merged_us_news:
#     news['published_date'] = format_published_date(news['published_date'])

# Convert the merged news to us_news.json
us_news_json = json.dumps(sorted_merged_us_news, indent=4)

# Write to json
with open(us_news_json_file, "w") as outfile:
    outfile.write(us_news_json)

