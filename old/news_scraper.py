import getopt
import sys
import json
import datetime
from newspaper import Article


def scrape_news(news_url, language='en', nlp=True):

    news = Article(news_url, language=language, MAX_KEYWORDS=15, MAX_AUTHORS=1)
    # download the document
    news.download()
    # parse text content
    news.parse()
    # run nlp for keywords
    if nlp:
        news.nlp()

    news_data = {}
    news_data['title'] = news.title
    news_data['authors'] = news.authors
    news_data['text'] = news.text
    news_data['language'] = news.meta_lang
    news_data['keywords'] = news.keywords
    news_data['tags'] = list(news.tags)
    news_data['url'] = news.url
    news_data['source'] = news.source_url
    news_data['publish_date'] = str(news.publish_date)
    news_data['scrape_date'] = str(datetime.datetime.now())

    return news_data


def save_result(news, file_name):
    with open(file_name+'.json', 'w') as outfile:
        json.dump(news, outfile)


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'x:f:l:nonlp')
    except getopt.GetoptError as err:
        # print help information and exit:
        print('err')
        sys.exit(2)

    news_url = None
    name_file = "results"
    language = 'en'
    nlp = True

    for o, a in opts:
        if o == "-x":
            news_url = a
        elif o == "-f":
            name_file = a
        elif o == "-l":
            language = a
        elif o == "-l":
            language = a
        elif o =="-nonlp":
            nlp = False

    if not news_url:
        print("You must provide a url to scrape.")
        return

    news = scrape_news(news_url, language, nlp)
    save_result(news, name_file)


if __name__ == "__main__":
    main()
