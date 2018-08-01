import tweepy
import json
from langdetect import detect
import csv
import sys
import getopt
import datetime
import modules.news_tweet_filter as url_filter
import modules.enrich_news_tweet as categorizer

'''
To run **get_tweets.py** you have to give these options:

-f : file name from which you want to get users' names
-o : file name in which you want to save users' tweets
'''


#login to twitter you must have a file called credentialsTwitter.json with your consumer_key, consumer_secret, access_token, access_token_secret
def login():
    fileKeys = open('credentialsTwitter.json').read()
    
    keys = json.loads(fileKeys)
    auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
    auth.set_access_token(keys['access_token'], keys['access_token_secret'])
    twitter = tweepy.API(auth, wait_on_rate_limit=True)
    return twitter


def user_tweets_to_mongo(account, twitter, mongo, sources, N=3000):
    max_number = 3200
    max_per_request = 50
    languages = ("de", "en", "es", "fr", "it", "pt")
    user_tweets = []
    if N > max_number:
        N = max_number
        iteration = 16
        last = 0
    else:
        iteration, last = divmod(N, max_per_request)
    user_timeline = twitter.user_timeline(screen_name=account, count=1, include_rts=True, tweet_mode="extended")
    if (user_timeline):
        for i in range(iteration+1):
            lastTweetId = int(user_timeline[-1].id_str)
            user_timeline = twitter.user_timeline(screen_name=account, max_id=lastTweetId, count=max_per_request, include_rts=True, tweet_mode="extended")
            for tweets in user_timeline:
                if tweets.lang == None:
                    tweets.lang = detect(tweets.text.replace("\n", " "))
                if tweets.lang in languages:
                    d = {'id_user': tweets.user.id_str, 'screen_name': tweets.user.screen_name.lower(), 'text': tweets.full_text, 'lang': tweets.lang, 'favourite_count': tweets.favorite_count, 'retweet_count': tweets.retweet_count, 'create_at': tweets.created_at.strftime("%Y-%m-%d %H:%M:%S"), 'mentions': tweets.entities['user_mentions'], '_id': tweets.id_str, 'coordinates': tweets.coordinates}
                    user_tweets.append(d)
            if i != iteration:
                user_tweets = user_tweets[:len(user_tweets)-1]
            if len(user_timeline) < max_per_request:
                break

    n_total = len(user_tweets)

    # extract url from tweets
    filtered_tweets = []
    for t in user_tweets:
        links = url_filter.text_contains_known_url(t['text'], sources)
        if len(links['urls']) > 0:
            t['urls'] = links['urls']
            t['news_sources'] = links['sources']
            t['article'] = []
            categorizer.process_tweet(t, sources)
            category = t['article']['category']
            print(t['urls'][0])
            print(category)
            if category and not mongo['categories'].find_one({'_id': category}):
                mongo['categories'].insert_one({'_id': category})
                print('New category: ' + category)
            filtered_tweets.append(t)

    user_tweets = filtered_tweets[:N]
    n_useful = len(user_tweets)

    for t in user_tweets:
        if not mongo['tweet'].find_one({'_id': t['_id']}):
            mongo['tweet'].insert_one(t)
    return {'total': n_total, 'useful': n_useful}


def user_tweets_to_mongo_urlex(account, twitter, mongo, sources, N=3000):
    max_number = 3200
    max_per_request = 200
    languages = ['en']
    user_tweets = []
    if N > max_number:
        N = max_number
        iteration = 16
        last = 0
    else:
        iteration, last = divmod(N, max_per_request)

    user_timeline = twitter.user_timeline(screen_name=account, count=1, include_rts=True, tweet_mode="extended")
    if user_timeline:
        for i in range(iteration + 1):
            lastTweetId = int(user_timeline[-1].id_str)
            user_timeline = twitter.user_timeline(screen_name=account, max_id=lastTweetId, count=max_per_request,
                                                  include_rts=True, tweet_mode="extended")
            for tweets in user_timeline:
                if not tweets.lang:
                    tweets.lang = detect(tweets.text.replace("\n", " "))
                if tweets.lang in languages:
                    d = {'id_user': tweets.user.id_str, 'screen_name': tweets.user.screen_name.lower(),
                         'text': tweets.full_text, 'lang': tweets.lang, 'favourite_count': tweets.favorite_count,
                         'retweet_count': tweets.retweet_count,
                         'create_at': tweets.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                         'mentions': tweets.entities['user_mentions'], '_id': tweets.id_str,
                         'coordinates': tweets.coordinates}
                    user_tweets.append(d)
            if i != iteration:
                user_tweets = user_tweets[:len(user_tweets) - 1]
            if len(user_timeline) < max_per_request:
                break

    n_total = len(user_tweets)

    tweets_with_link = []
    expander_query = ''
    for i in range(0, len(user_tweets)):
        link = url_filter.extract_raw_link(user_tweets[i]['text'])
        if link and link != '':
            user_tweets[i]['link_raw'] = link
            tweets_with_link.append(user_tweets[i])
            expander_query = expander_query + link + '***'

    expanded_links = url_filter.expand(expander_query)

    for i in range(0, len(tweets_with_link)):
        tweets_with_link[i]['news_url'] = expanded_links[i]

    filtered_tweets = []
    for t in tweets_with_link:
        t = url_filter.extract_known_sources(t, sources)
        if 'news_source' in t:
            filtered_tweets.append(t)

    user_tweets = filtered_tweets[:N]
    n_useful = len(user_tweets)

    for t in user_tweets:
        if not mongo['tweet'].find_one({'_id': t['_id']}):
            mongo['tweet'].insert_one(t)
    return {'total': n_total, 'useful': n_useful}


def get_tweets(twitter, account, N, start_date=None, end_date=None):
    max_number = 3200
    max_per_request = 200
    languages = ("de", "en", "es", "fr", "it", "pt")
    user_tweets = []
    if N > max_number:
        N = max_number
        iteration = 16
        last = 0
    else:
        iteration, last = divmod(N, max_per_request)
    user_timeline = twitter.user_timeline(screen_name=account, count=1, include_rts=False, tweet_mode="extended")
    if (user_timeline):
        for i in range(iteration+1):
            lastTweetId = int(user_timeline[-1].id_str)
            user_timeline = twitter.user_timeline(screen_name=account, max_id=lastTweetId, count=max_per_request, include_rts=False, tweet_mode="extended")
            for tweets in user_timeline:
                if tweets.lang == None:
                    tweets.lang = detect(tweets.text.replace("\n", " "))
                if tweets.lang in languages:
                    d = {'id_user': tweets.user.id_str, 'screen_name': tweets.user.screen_name.lower(), 'text': tweets.full_text, 'lang': tweets.lang, 'favourite_count': tweets.favorite_count, 'retweet_count': tweets.retweet_count, 'create_at': tweets.created_at.strftime("%Y-%m-%d %H:%M:%S"), 'mentions': tweets.entities['user_mentions'], '_id': tweets.id_str, 'coordinates': tweets.coordinates}
                    user_tweets.append(d)
            if i != iteration:
                user_tweets = user_tweets[:len(user_tweets)-1]
            if len(user_timeline) < max_per_request:
                break
    else:
        print('no tweets')

    print(account, len(user_tweets))
    return user_tweets[:N]

def get_tweets_from_users(file_users, twitter):
    users = csv.reader(open(file_users, 'r'))
    all_tweets = {}
    for u in users:
        all_tweets[u[0]] = get_tweets(twitter, u[0], 200)
    return all_tweets


def save_tweets(all_tweets, file_out_name):
    j = json.dumps(all_tweets)
    file = open(file_out_name,'w')
    file.write(j)

def main():
    timeStart = datetime.datetime.now()

    try:
        twitter = login()
    except:
        print('no login twitter')
        return
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'f:o:')
    except getopt.GetoptError as err:
        # print help information and exit:
        print('err')  # will print something like "option -a not recognized"
        #        usage()
        sys.exit(2)
    file_users = None
    file_out_name = None
    for o, a in opts:
        if o == "-f":
            file_users = a
        elif o == "-o":
            file_out_name = a
    all_tweets = get_tweets_from_users(file_users, twitter)
    save_tweets(all_tweets, file_out_name)


if __name__ == "__main__":
    timeStart = datetime.datetime.now()
    main()
    timeEnd = datetime.datetime.now()
    delta = timeEnd - timeStart
    print('-- Executed in ' + str(int(delta.total_seconds())) + 's')

