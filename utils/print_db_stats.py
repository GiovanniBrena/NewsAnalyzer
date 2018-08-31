import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
dbc = client["NewsAnalyzer"]

cat = ['world', 'politics', 'business', 'sports', 'entertainment/art', 'national/local', 'style/food/travel', 'science/technology/health']
print('[ALL] Articles count: ' + str(dbc.articles.find().count()))
print('[GROUND TRUTH] Articles count: ' + str(dbc.articles.find({'ground_truth': True}).count()))
for cc in cat:
    print('[GROUND TRUTH] ' + cc + ': ' + str(dbc.articles.find({'ground_truth': True, 'category_aggregate': cc}).count()))

