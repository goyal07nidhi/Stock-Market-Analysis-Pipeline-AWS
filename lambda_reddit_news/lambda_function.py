from datetime import datetime
from io import StringIO
from configparser import ConfigParser
import boto3
import json
import os
import requests
import pandas as pd


def df_from_response(res):
    """
     return a transformed dataframe for the reddit data
    """
    # initialize temp dataframe for batch of data in response
    df = pd.DataFrame()
    # loop through each post pulled from res and append to df
    for post in res.json()['data']['children']:
        df = df.append({
            'subreddit': post['data']['subreddit'],
            'title': post['data']['title'],
            'selftext': post['data']['selftext'],
            'upvote_ratio': post['data']['upvote_ratio'],
            'ups': post['data']['ups'],
            'downs': post['data']['downs'],
            'score': post['data']['score'],
            'link_flair_css_class': post['data']['link_flair_css_class'],
            'created_utc': datetime.fromtimestamp(post['data']['created_utc']).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'id': post['data']['id'],
            'kind': post['kind']
        }, ignore_index=True)
    return df


def lambda_handler(event, context):
    """
        1.Collects data from Reddit
        2.Loads the Datafile to the S3 bucket
        3.return a response for the Lex bot
    """

    bucket = os.environ['ip_bucket']
    s3_key = os.environ['s3_key']
    s3 = boto3.resource('s3')

    # Download Config File
    s3.Bucket(bucket).download_file('config/config.ini', '/tmp/config.ini')
    print('Config File Downloaded')

    config = ConfigParser()
    config.read('/tmp/config.ini')
    print('Config File Parsed')

    # authenticate API
    client_auth = requests.auth.HTTPBasicAuth(config.get('reddit', 'CLIENT_ID'),
                                              config.get('reddit', 'CLIENT_SECRET_ID'))
    data = {'grant_type': 'password', 'username': config.get('reddit', 'USERNAME'),
            'password': config.get('reddit', 'PASSWORD')}
    headers = {'User-Agent': 'MyBot/0.0.1'}

    # send authentication request for OAuth token
    res = requests.post('https://www.reddit.com/api/v1/access_token', auth=client_auth, data=data, headers=headers)
    TOKEN = f"bearer {res.json()['access_token']}"
    headers = {**headers, **{'Authorization': TOKEN}}

    data = pd.DataFrame()
    params = {'limit': 100}
    print("Loading data to csv file..")

    try:
        for i in range(0, 1):
            # make request
            res = requests.get("https://oauth.reddit.com/r/wallstreetbets/hot",
                               headers=headers, params=params)
            # get dataframe from response
            new_df = df_from_response(res)
            # take the final row (oldest entry)
            row = new_df.iloc[len(new_df) - 1]
            # create fullname
            fullname = row['kind'] + '_' + row['id']
            # add/update fullname in params
            params['after'] = fullname
            # append new_df to data
            data = data.append(new_df, ignore_index=True)
    except:
        pass
    print("Loading data to S3..")
    # load the dataframe as .csv file to S3
    csv_buffer = StringIO()
    data.to_csv(csv_buffer)
    s3_resource = boto3.resource('s3', region_name=config.get('aws', 'REGION_NAME'), aws_access_key_id=config.get('aws', 'ACCESS_KEY'), aws_secret_access_key=config.get('aws', 'SECRET_KEY'))
    s3_resource.Object(bucket, s3_key).put(Body=csv_buffer.getvalue())
    print("Successful")
    result = {
        "sessionAttributes": {},
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
            "message": {
                "contentType": "PlainText",
                "content": "Thank you for your response! If you would like to see trending stocks, please write 'Reddit Stock' in the chatbox."
            }
        }
    }
    return result
