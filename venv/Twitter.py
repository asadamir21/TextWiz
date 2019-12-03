import tweepy
import csv
import pandas as pd
####input your credentials here
consumer_key = 's3MT03IsWkMrTj41HxH6InNzr'
consumer_secret = 'jaqHc7GLjmxaM8xITLHWdcHC10nhzPXfG6RTwtUOmAJo673nRg'
access_token = '1115595365380550659-1q2eKGnzYESKSujOTKQ16fhWbHRWAk'
access_token_secret = 'le5JNnMhFM3iLbbRODsJyLblIZCltKwwjIXsdVokxsG20'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth,wait_on_rate_limit=True)
for tweet in tweepy.Cursor(api.search,q="#unitedAIRLINES",count=100,
                           lang="en",
                           since="2017-04-03").items():
    print(tweet)
    #print (tweet.created_at, tweet.text, tweet)
    #csvWriter.writerow([tweet.created_at, tweet.text.encode('utf-8')])
