import modules.enrich_news_tweet as enricher
import pymongo
import threading
import modules.article_scraper as scraper
from threading import Thread
import time
from random import randint


mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo_client["NewsAnalyzer"]
url = 'https://eu.usatoday.com/story/news/politics/2018/09/02/john-mccain-buried-naval-academy-after-weekend-tributes/1180358002/'

print(scraper.scrape_news(url))

