import newspaper
import json
import pymongo
import pickle
import modules.news_scraper as news_scraper
import modules.category_classifier as classifier


mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo_client["NewsAnalyzer"]

fileSources = open('data/sources.json').read()
sources = json.loads(fileSources)

category_list = db['categories'].distinct('category')

# load the model from disk
models = {}
models['model'] = pickle.load(open('models/classifier.sav', 'rb'))
models['countvect'] = pickle.load(open('models/countvect.sav', 'rb'))
models['tfidfvect'] = pickle.load(open('models/tfidfvect.sav', 'rb'))
models['labelencoder'] = pickle.load(open('models/labelencoder.sav', 'rb'))

domain = 'https://www.nypost.com'

news_source = newspaper.build(domain, memoize_articles=False)
print('Found articles: ' + str(news_source.size()))
for article in news_source.articles:
    try:
        url = article.url
        news_data = news_scraper.scrape_news(url)
        print(url)
        print(classifier.predict(news_data['keywords'], 10, models))
    except:
        pass

