import tweepy
import time
from langdetect import detect
import modules.news_tweet_filter as url_filter
import modules.enrich_news_tweet as enricher


def user_tweets_to_mongo(account, twitter, mongo, sources, N=3000):
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

    try:
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
    except tweepy.RateLimitError:
        print('TWITTER LIMIT REACHED: sleep for 15 mins')
        time.sleep(15 * 60)

    n_total = len(user_tweets)

    tweets_with_link = []
    expander_query = ''
    for i in range(0, len(user_tweets)):
        if not mongo['tweet'].find_one({'_id': user_tweets[i]['_id']}):
            link = url_filter.extract_raw_link(user_tweets[i]['text'])
            if link and link != '':
                user_tweets[i]['link_raw'] = link
                tweets_with_link.append(user_tweets[i])
                expander_query = expander_query + link + '***'

    print(account + ' : [URLS] expanding links, count ' + str(len(expander_query.split('***'))))
    expanded_links = url_filter.expand(expander_query)
    for i in range(0, len(tweets_with_link)):
        if len(expanded_links) > i:
            tweets_with_link[i]['news_url'] = expanded_links[i]

    filtered_tweets = []
    for t in tweets_with_link:
        t = url_filter.extract_known_sources(t, sources)
        if 'news_source' in t:
            filtered_tweets.append(t)

    user_tweets = filtered_tweets[:N]
    n_useful = len(user_tweets)

    # download articles and store tweet + article
    print(account + ' : [ARTICLES] start processing, count ' + str(n_useful))
    for t in user_tweets:
        t = enricher.process_tweet(t, mongo)
        if t and not mongo['tweet'].find_one({'_id': t['_id']}):
            mongo['tweet'].insert_one(t)
    return {'total': n_total, 'useful': n_useful}

