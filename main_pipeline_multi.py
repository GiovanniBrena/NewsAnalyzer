import sys
import datetime
import pymongo
import json
import modules.twitter_login as twitter_login
import modules.news_extractor as news_extractor
import modules.user_scraper as user_scraper
import modules.get_tweets as get_tweets
sys.path.append("/modules")
sys.path.append("/data")

# Parameters
ART_PER_CATEGORY = 5

MAX_USERS = 100
MAX_TWEETS = 200

'''
Pipeline steps:
1) Extract twitter usernames from news url
2) Exctract user accounts and update users collection
3) Extract tweets + articles
    [foreach user]
    - filter tweets from known news sources
        [foreach tweet]
            - run sentiment analysis on text
            - scrape news article
            - categorize article
            - update articles collection
            - update tweet collection
'''


def main():
    try:
        twitter = twitter_login.login()
    except:
        print('no login twitter')
        return
    try:
        mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = mongo_client["NewsAnalyzer"]
    except:
        print('no mongodb')
        return

    # sample random articles from each category from DB
    articles = []
    categories = ['world', 'politics', 'business', 'sports', 'entertainment/art', 'national/local', 'style/food/travel', 'science/technology/health']
    # categories = ['business', 'national/local', 'style/food/travel', 'sports']

    for c in categories:
        sample = list(db.articles.aggregate([{"$match": {"category_aggregate": c, "pipelined": False, "ground_truth": True}},
                                             {"$sample": {"size": ART_PER_CATEGORY}}]))
        articles.extend(sample)

    total_tw_processed = 0
    total_tw_useful = 0

    # run pipeline foreach sample
    for art in articles:
        news_url = art['url']
        print('Processing article: ' + news_url)
        # 1
        # extract sharing user names from url
        user_names = news_extractor.get_users_from_news(news_url, twitter, MAX_USERS-1)
        if len(user_names) == 0:
            db.articles.update({"_id": art["_id"]}, {"$set": {"pipelined": True}})
            print('No users found. Skip article.')
            continue
        print('Users count: ' + str(len(user_names)))

        # 2
        # store users information
        for u in user_names:
            user_scraper.user_to_mongo(u, twitter, db)

        # 3
        # extract tweets by users
        print('Extracting tweets...')
        tw_total = 0
        tw_useful = 0
        file_sources = open('data/sources.json').read()
        sources = json.loads(file_sources)
        for u in user_names:
            count = get_tweets.user_tweets_to_mongo(u, twitter, db, sources, MAX_TWEETS)
            tw_total = tw_total + count['total']
            tw_useful = tw_useful + count['useful']
            print('| ' + u + ' useful tweets: ' + str(count['useful']) + ' / ' + str(count['total']))

        if tw_useful > 0:
            print('Total useful tweets: ' + str(tw_useful) + ' / ' + str(tw_total) + ' (' + str(round((tw_useful/tw_total)*100, 2)) + '%)')

        db.articles.update({"_id": art["_id"]}, {"$set": {"pipelined": True}})

        total_tw_processed = total_tw_processed + tw_total
        total_tw_useful = total_tw_useful + tw_useful

    print_results(total_tw_processed, total_tw_useful, db)


def print_results(total, useful, db):
    if total == 0:
        total = 1
    print('-----------------------------------------------------------------')
    print('PIPELINE END')
    print('Total useful tweets: ' + str(useful) + ' / ' + str(total) + ' (' + str(
        round((useful / total) * 100, 2)) + '%)')
    print('DATABASE')
    print('Users count: ' + str(db.user.count()))
    print('Tweets count: ' + str(db.tweet.count()))
    print('Articles count: ' + str(db.articles.count()))
    print('-----------------------------------------------------------------')


if __name__ == "__main__":
    timeStart = datetime.datetime.now()
    main()
    timeEnd = datetime.datetime.now()
    delta = timeEnd - timeStart
    print('Executed in ' + str(int(delta.total_seconds())) + 's')

