
import json
import re
import sys
import getopt
import requests
import datetime
import modules.news_scraper as news_scraper

'''
This script enrich tweets by adding a category from url (if present) and a set of keywords.
To run enrich_news_tweet.py you have to give these options:

-x : input user tweet json array
-s : news sources json array
-o : output file name
'''

def enrich_news_tweets(input_file, sources_file):
    fileTweets = open(input_file).read()
    tweets = json.loads(fileTweets)

    for user in tweets:
        tw_count = 0
        print('Processing ' + user)
        for tw in tweets[user]:
            tw = process_tweet(tw, sources_file)
            tw_count=tw_count+1
            print(str(tw_count) + ' / ' + str(len(tweets[user])))
    return tweets


def save_tweets(data, name_file):
    j = json.dumps(data)
    file = open(name_file, 'w')
    file.write(j)
    return


def process_tweet(tweet, sources):
    url = tweet['urls'][0]
    source_name = tweet['news_sources'][0]
    category = None

    news_data = news_scraper.scrape_news(url)

    for s in sources:
        if source_name == s['name'] and s['url_category'] == 'True':
            splitted_url = url.split('/')
            if len(splitted_url) > int(s['url_category_position']):
                category = splitted_url[int(s['url_category_position'])]
            if category == 'news':
                category = url.split('/')[int(s['url_category_position'])+1]

    '''
    if source == 'The Wall Street Journal':
        category = None

    elif source == 'The New York Times':
        category = url.split('/')[6]

    elif source == 'USA Today':
        category = url.split('/')[4]
        if category == 'news':
            category = url.split('/')[5]

    elif source == 'Los Angeles Times':
        category = url.split('/')[3]

    elif source == 'The Mercury News':
        category = None

    elif source == 'New York Daily News':
        category = url.split('/')[4]

    elif source == 'New York Post':
        category = None

    elif source == 'The Washington Post':
        category = url.split('/')[3]

    elif source == 'Chicago Sun-Times':
        category = url.split('/')[3]

    elif source == 'The Denver Post':
        category = None

    elif source == 'Chicago Tribune':
        category = None

    elif source == 'The Dallas Morning News':
        category = url.split('/')[4]

    elif source == 'Newsday':
        category = url.split('/')[3]

    elif source == 'Huston Chronicles':
        category = url.split('/')[3]

    elif source == 'Orange County Register':
        category = None
    elif source == 'The Star-Ledger':
        category = None
    elif source == 'Tampa Bay Times':
        category = None
    elif source == 'The Plain Dealer':
        category = None
    elif source == 'The Philadelphia Inquier':
        category = None
    elif source == 'Star Tribune':
        category = None
    elif source == 'The Arizona Republic':
        category = url.split('/')[4]
        if category == 'news':
            category = url.split('/')[5]
            
    elif source == 'Honolulu Star-Advertiser':
        category = None
    elif source == 'Las Vegas Review-Journal':
        category = None
    elif source == 'The San Diego Union-Tribune':
        category = None
    elif source == 'The Boston Globe':
        category = None
    elif source == 'CNN':
        category = None
    elif source == 'Fox News':
        category = None
    elif source == 'MSNBC':
        category = None
    elif source == 'NBC News':
        category = None
    elif source == 'ABC News':
        category = None
    elif source == 'CBS News':
        category = None
    elif source == 'The Blaze':
        category = None
    elif source == 'Al Jazeera':
        category = None
    elif source == 'Bloomberg News':
        category = None
    elif source == 'Voice of America':
        category = None
    elif source == 'United Press International':
        category = None
    elif source == 'Politico':
        category = None
    elif source == 'NPR News':
        category = None
    elif source == 'Breitbart News Network':
        category = None
    elif source == 'The Onion':
        category = None
    elif source == 'Newsmax':
        category = None
    elif source == 'Newsweek':
        category = None

    '''
    news_data['category'] = category
    tweet['article'] = news_data



def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'x:s:o:')
    except getopt.GetoptError as err:
        # print help information and exit:
        print('err')  # will print something like "option -a not recognized"
        #        usage()
        sys.exit(2)
    input_file = None
    sources_file = None
    output_file = None
    for o, a in opts:
        if o == "-x":
            input_file = a
        elif o == "-s":
            sources_file = a
        elif o == "-o":
            output_file = a

    enriched_tweets = enrich_news_tweets(input_file, sources_file)
    save_tweets(enriched_tweets, output_file)


if __name__ == "__main__":
    timeStart = datetime.datetime.now()
    main()
    timeEnd = datetime.datetime.now()
    delta = timeEnd - timeStart
    print('Executed in ' + str(int(delta.total_seconds())) + 's')
