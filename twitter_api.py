#!/usr/bin/env python

import calendar
import time
import pickle

import twitter

from auth import TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN_KEY, TWITTER_ACCESS_TOKEN_SECRET, TWITTER_STOCK_USERNAME
from const import FOLLOWERS_FILE_PATH

api = twitter.Api(consumer_key=TWITTER_CONSUMER_KEY,
                  consumer_secret=TWITTER_CONSUMER_SECRET,
                  access_token_key=TWITTER_ACCESS_TOKEN_KEY,
                  access_token_secret=TWITTER_ACCESS_TOKEN_SECRET)


def get_statuses_since_id(id):
    return api.GetUserTimeline(screen_name=TWITTER_STOCK_USERNAME, since_id=id, count=200, exclude_replies=True)


def get_status_for_first_tweet_of_day():
    statuses = api.GetUserTimeline(screen_name=TWITTER_STOCK_USERNAME, count=200, exclude_replies=True)
    current_time = calendar.timegm(time.gmtime()) # around 9am EST, 6am PST
    current_time -= 3600 # lets start an hour before
    reference_status = None

    for status in statuses:
        if status.created_at_in_seconds < current_time:
            reference_status = status
            break

    return reference_status


def get_followers():
    followers_list = []
    follower_ids = api.GetFollowerIDs(screen_name=TWITTER_STOCK_USERNAME)
    followers = return_users_from_ids(follower_ids, api)
    blacklist = ['fitz', 'worldsceo', 'itradestox1', 'badnewsbees2005', 'tradestoxnow', 'kevinbanks77', 'mattth', 'charlie4czunz', 'rorotrader']

    for follower in followers:
        blacklisted = False
        for item in blacklist:
            if item in follower.lower():
                blacklisted = True
                break
        if not blacklisted:
            followers_list.append(follower)

    return followers_list


def return_users_from_ids(user_ids, current_api):
    all_users = []
    id_chunks = chunks(user_ids, 100)
    for item in id_chunks:
        users = current_api.UsersLookup(user_id=item)
        for user in users:
            all_users.append(user.screen_name)
    return all_users


def dump_followers_to_file():
    with open(FOLLOWERS_FILE_PATH, 'wb') as fp:
        pickle.dump(get_followers(), fp)


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
