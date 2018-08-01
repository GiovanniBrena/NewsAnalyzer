import newspaper
import json
import pymongo
import modules.news_scraper as news_scraper
import requests

r = requests.get('http://1vxhpyp8tevqb7ld.pro.urlex.org/json/http://bit.ly/iiLcUI******http://bit.ly/iiLcUI***')
if r:
    response = r.json()
    for i in response:
        print(i['longurl'])


