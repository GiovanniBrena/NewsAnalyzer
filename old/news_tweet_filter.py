from urllib.parse import urlparse
from http import client
import json
import re
import sys
import getopt
import requests
import datetime

'''
This script filter a json array of user tweets based on the presence of news links
To run news_tweet_filter.py you have to give these options:

-x : input user tweet json array
-s : news sources json array
-o : output file name
'''

urlex_endpoint = "http://1vxhpyp8tevqb7ld.pro.urlex.org/json/"


def filter_news_tweets(input_file, sources_file):
    filtered = {}

    fileSources = open(sources_file).read()
    sources = json.loads(fileSources)

    fileTweets = open(input_file).read()
    tweets = json.loads(fileTweets)

    # for each user in the list
    for user in tweets:
        print('Processing ' + user)
        filtered[user] = []
        tw_count = 0
        # for each tweet of the user
        for tw in tweets[user]:
            tw['urls'] = find_urls_in_text(tw['text'])
            # for each url found in text
            for u in tw['urls']:
                # for each source
                for s in sources:
                    domain = s['domain'].split('//', 1)[1]
                    if domain in u:
                        tw['source'] = s['name']
                        filtered[user].append(tw)
            tw_count = tw_count + 1
            print(str(tw_count) + ' / ' + str(len(tweets[user])))

    return filtered


def text_contains_known_url(t, sources):
    known_urls = []
    sources_found = []
    #print(t)
    urls = find_urls_in_text(t)
    for u in urls:
        for s in sources:
                for d in s['domain']:
                    if u and d in u:
                        known_urls.append(u)
                        sources_found.append(s['name'])
    return {'urls': known_urls, 'sources': sources_found}


def find_urls_in_text(text):
    # look for http links
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    splitted_urls = []
    for u in urls:
        splitted_urls.extend(u.split(' '))
    urls = splitted_urls
    expanded_urls = []
    for u in urls:
        expanded_urls.append(unshorten_url(u))
    return expanded_urls


def unshorten_url(url, count=0):
    try:
        parsed = urlparse(url)
        h = client.HTTPConnection(parsed.netloc)
        resource = parsed.path
        if parsed.query != "":
            resource += "?" + parsed.query
        h.request('HEAD', resource)
        response = h.getresponse()
        if response.status // 100 == 3 and response.getheader('Location') and count < 3:
            return unshorten_url(response.getheader('Location'), count+1)  # changed to process chains of short urls
        else:
            return url
    except:
        return url


def extract_raw_link(text):
    # look for http links
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    splitted_urls = []
    for u in urls:
        splitted_urls.extend(u.split(' '))
    if len(splitted_urls) > 0:
        return splitted_urls[0]
    else:
        return None


def expand(query):
    result = []
    r = requests.get(urlex_endpoint+query)
    if r:
        response = r.json()
        for i in response:
            result.append(i['longurl'])
    return result


def extract_known_sources(tweet, sources):
    u = tweet['news_url']
    for s in sources:
        for d in s['domain']:
            if u and d in u:
                tweet['news_source'] = s['name']
    return tweet


def save_tweets(data, name_file):
    j = json.dumps(data)
    file = open(name_file, 'w')
    file.write(j)
    return


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

    filtered_tweets = filter_news_tweets(input_file,sources_file)
    save_tweets(filtered_tweets, output_file)


if __name__ == "__main__":
    timeStart = datetime.datetime.now()
    main()
    timeEnd = datetime.datetime.now()
    delta = timeEnd - timeStart
    print('-- Executed in ' + str(int(delta.total_seconds())) + 's')
