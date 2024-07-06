from gnews import GNews
from newspaper import Article, ArticleException
import json

# Config GNews
google_news = GNews()
google_news.country = 'United States'
google_news.language = 'English'
google_news.start_date = (2024, 1, 1)
google_news.max_results = 10

# Fetch news using GNews
us_news = google_news.get_news('United State Election')

temp_us_news = us_news

for news in us_news:
    article = Article(news['url'])
    try:
        article.download()
        article.parse()
        news['image_url'] = article.top_image
    except ArticleException:
        print('failed to download from', news['url'])
        continue

# Convert to json
us_news_json = json.dumps(us_news, indent=4)

# Write to json
with open("us_news.json", "w") as outfile:
    outfile.write(us_news_json)

