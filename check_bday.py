#!/usr/bin/python3

import pandas as pd
import datetime
import tweepy
import os
import requests
from dotenv import load_dotenv
from instadm import InstaDM

tweet = ""
insta = ""
df = pd.read_csv("/home/gabe/birthdaybot/birthdays.csv")
today = datetime.datetime.now().strftime("%m-%d")
for index, item in df.iterrows():
    bday = item['Birthday']
    if(bday == today and item['Twitter'] != 'na'):
        print(item['Name'] + "'s birthday")
        tweet = (item['Twitter'] + " happy birthday!")
    elif(bday == today and item['Instagram'] != 'na'):
        insta = item['Instagram']
    elif(bday == today):
        resp = requests.post('https://textbelt.com/text', {
            'phone': 'your_phone_no',
            'message': item['Name'] + '\'s birthday',
            'key': os.getenv("TBKEY"),
        })
        print(resp.json())
if (tweet != ""):
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(os.getenv("APIKEY"), os.getenv("APISECRET"))
    auth.set_access_token(os.getenv("TOKEN"), os.getenv("TOKENSECRET"))
    api = tweepy.API(auth)
    # tweet
    api.update_status(tweet)
    print(tweet)

if (insta != ""):
    # instagram auth
    instamsg = InstaDM(username=os.getenv("INSTAUSER"),
                       password=os.getenv("INSTAPASS"), headless=True)
    # dm user
    instamsg.sendMessage(user=insta, message='happy birthday!')
    print(insta)
