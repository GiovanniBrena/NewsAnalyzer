import getopt
import sys
import json
import datetime
from newspaper import Article


def scrape_news(news_url, language='en', nlp=True):
    try:
        news = Article(news_url, language=language, MAX_KEYWORDS=30, MAX_AUTHORS=1, fetch_images=False)
        # download the document
        news.download()
        # parse text content
        news.parse()
        # run nlp for keywords
        if nlp:
            news.nlp()

        news_data = {}
        news_data['_id'] = news.url.encode('utf-8').hex()[-64:]
        news_data['title'] = news.title
        news_data['authors'] = news.authors
        news_data['text'] = news.text
        news_data['language'] = news.meta_lang
        news_data['keywords'] = news.keywords
        news_data['tags'] = list(news.tags)
        news_data['url'] = news.url
        news_data['source'] = news.source_url
        news_data['publish_date'] = str(news.publish_date)
        news_data['scrape_date'] = str(datetime.datetime.now())
        news_data['pipelined'] = False

        return news_data
    except:
        return None

