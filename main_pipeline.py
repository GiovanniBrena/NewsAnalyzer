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
news_url = 'https://www.nytimes.com/2018/07/29/us/carr-fire-victim-california.html'
MAX_USERS = 100
MAX_TWEETS = 100


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

    # 1
    # extract sharing user names from url
    user_names = news_extractor.get_users_from_news(news_url, twitter, MAX_USERS-1)
    if len(user_names)==0:
        print('No users found. Close pipeline.')
        return
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
        print(u + ' useful tweets: ' + str(count['useful']) + ' / ' + str(count['total']))

    if tw_useful > 0:
        print('Total useful tweets: ' + str(tw_useful) + ' / ' + str(tw_total) + ' (' + str(round((tw_useful/tw_total)*100, 2)) + '%)')


if __name__ == "__main__":
    timeStart = datetime.datetime.now()
    main()
    timeEnd = datetime.datetime.now()
    delta = timeEnd - timeStart
    print('Executed in ' + str(int(delta.total_seconds())) + 's')

