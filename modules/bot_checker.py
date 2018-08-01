import botometer
import json

def bot_check_by_id(userId):
    fileKeys = open('credentialsTwitter.json').read()
    keys = json.loads(fileKeys)

    mashape_key = keys['mashape_key']
    twitter_app_auth = {
        'consumer_key': keys['consumer_key'],
        'consumer_secret': keys['consumer_secret'],
        'access_token': keys['access_token'],
        'access_token_secret': keys['access_token_secret'],
      }
    bom = botometer.Botometer(wait_on_ratelimit=True,
                              mashape_key=mashape_key,
                              **twitter_app_auth)

    # Check a single account by id
    result = bom.check_account(userId)
    return result


def bot_check_by_screenname(userId):
    fileKeys = open('credentialsTwitter.json').read()
    keys = json.loads(fileKeys)

    mashape_key = keys['mashape_key']
    twitter_app_auth = {
        'consumer_key': keys['consumer_key'],
        'consumer_secret': keys['consumer_secret'],
        'access_token': keys['access_token'],
        'access_token_secret': keys['access_token_secret'],
    }
    bom = botometer.Botometer(wait_on_ratelimit=True,
                              mashape_key=mashape_key,
                              **twitter_app_auth)

    # Check a single account by id
    result = bom.check_account('@'+userId)
    return result

