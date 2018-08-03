import json
import sys
import getopt
import datetime
import modules.article_scraper as news_scraper

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
            process_tweet(tw, sources_file)
            tw_count = tw_count+1
            print(str(tw_count) + ' / ' + str(len(tweets[user])))
    return tweets


def save_tweets(data, name_file):
    j = json.dumps(data)
    file = open(name_file, 'w')
    file.write(j)
    return


def process_tweet(tweet, db):
    url = tweet['urls'][0]
    source_name = tweet['news_sources'][0]

    news_data = news_scraper.scrape_news(url)
    category = extract_category_from_url(url, source_name, db)
    # if category == None: predict

    news_data['category'] = category
    tweet['article'] = news_data


def extract_category_from_url(url, source_name, db):
    category = None
    sources = db.sources.find()
    for s in sources:
        if source_name == s['name'] and s['url_category'] == 'True':
            splitted_url = url.split('/')
            if len(splitted_url) > int(s['url_category_position']):
                category = splitted_url[int(s['url_category_position'])]
            if (category == 'news' or category == 'us') and len(splitted_url) > int(s['url_category_position']) + 1:
                category = url.split('/')[int(s['url_category_position']) + 1]
            return get_consolidated_category(category, db)
    return None


def get_consolidated_category(raw_category, db):
    category_row = db.categories.find_one({'_id': raw_category})
    if category_row:
        return category_row['category']
    else:
        return None


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
