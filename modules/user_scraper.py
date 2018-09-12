from tweepy import TweepError
import pymongo as pym

def user_to_mongo(username, twitter, db):

    # check if user is already known
    if db['user'].find_one({'screen_name': username}):
        print('Skipping user, account already known: ', username)
        return

    try:
        data = twitter.get_user(username)
        user = {}
        user['_id'] = data.id
        user['name'] = data.name
        user['screen_name'] = data.screen_name
        user['description'] = data.description
        user['location'] = data.location
        user['lang'] = data.lang
        user['profile_image_url'] = data.profile_image_url
        user['statuses_count'] = data.statuses_count
        user['friends_count'] = data.friends_count
        user['followers_count'] = data.followers_count
        user['favourites_count'] = data.favourites_count
        user['geo_enabled'] = data.geo_enabled
        user['url'] = data.url
        user['created_at'] = data.created_at

        # insert user into mongo
        try:
            db['user'].insert_one(user)
            print('Inserted user: ', username)
        except pym.errors.DuplicateKeyError:
            print('Duplicate user, skip')
            pass

    except TweepError as e:
        if e.api_code == 50:
            print('Skipping user, account not found for name:', username, ',', e)
        if e.api_code == 63:
            print('Skipping user, account is suspended for name:', username, ',', e)
        elif e.api_code == 88:
            print('Skipping user, rate limit exceeded,', e)
        else:
            print('Skipping user, not known error, for ID:', username, ',', e)

