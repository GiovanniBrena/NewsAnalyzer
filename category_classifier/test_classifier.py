import newspaper
import pymongo
import pickle
import sys
sys.path.append("..")
from twitter_pipeline import article_scraper as news_scraper
from category_classifier import category_classifier_v2 as classifier
from twitter_pipeline import enrich_news_tweet as enricher


'''
This script allows tests on a previously trained news category classifier:
- domain: source from where to scrape unseen data
- if domain has url_category the scripts evaluates predictions over real categories,
otherwise it just prints the url and the prediction
'''

SCRAPE_MODE = True
TEST_SIZE = 1000
EXCLUDE_SOURCE = ['The New York Times', 'CNN']
domain = 'nydailynews.com'


mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo_client["NewsAnalyzer"]

# load the model from disk
models = {}
models['model'] = pickle.load(open('../models/classifier.sav', 'rb'))
models['countvect'] = pickle.load(open('../models/countvect.sav', 'rb'))
# models['tfidfvect'] = pickle.load(open('../models/tfidfvect.sav', 'rb'))
models['labelencoder'] = pickle.load(open('../models/labelencoder.sav', 'rb'))

if SCRAPE_MODE:
    # retrieve news source from db
    if db.sources.find_one({'domain': domain}):
        source_name = db.sources.find_one({'domain': domain})['name']
    else:
        sys.exit("Bad domain. Close.")

    # scrape news source
    news_source = newspaper.build('https://www.' + domain, memoize_articles=False)
    print('Found articles: ' + str(news_source.size()))

    total_counter = 0
    true_positive = 0

    # scrape articles, predict category and update counters
    for article in news_source.articles:
        url = article.url
        try:
            news_data = news_scraper.scrape_news(url)
            if not news_data or not 'keywords' in news_data:
                continue
            kw = news_data['keywords']
            if len(news_data['tags']) > 2:
                kw.extend(news_data['tags'])
            print(url)
            prediction = classifier.predict(kw, models)
            print(prediction)
            extracted_category = classifier.get_aggregated_category(enricher.extract_category_from_url(url, source_name, db))
            if extracted_category and prediction:
                total_counter = total_counter + 1
                if extracted_category == prediction['class']:
                    true_positive = true_positive + 1
        except:
            pass

else:
    total_counter = 0
    true_positive = 0

    test_set = list(db.articles.aggregate([
        {"$match": {"ground_truth": True, "source_name": {'$nin': EXCLUDE_SOURCE}}},
        {"$sample": {"size": TEST_SIZE}}]))

    print('Actual test size: ' + str(len(test_set)))

    # scrape articles, predict category and update counters
    for article in test_set:
        url = article['url']
        try:
            if not article or not 'keywords' in article:
                continue
            kw = article['keywords']
            if len(article['tags']) > 2:
                kw.extend(article['tags'])
            print(url)
            prediction = classifier.predict(kw, models)
            print(prediction)
            extracted_category = classifier.get_aggregated_category(
                enricher.extract_category_from_url(url, article['source_name'], db))
            if extracted_category and prediction:
                total_counter = total_counter + 1
                if extracted_category == prediction['class']:
                    true_positive = true_positive + 1
        except:
            pass

# print accuracy
if total_counter > 0:
    print('----------- Prediction accuracy: ' + str(true_positive) + '/' + str(total_counter) +
          ' ( ' + str(round((true_positive / total_counter)*100, 2)) + '% )')
