import boto3
import os
import pandas as pd
from pandas import DataFrame
from configparser import ConfigParser


def lambda_handler(event, context):

    bucket = os.environ['ip_bucket']
    s3_key = os.environ['s3_key']
    s3 = boto3.resource('s3')

    # Download Config File
    s3.Bucket(bucket).download_file('config/config.ini', '/tmp/config.ini')
    print('Config File Downloaded')

    config = ConfigParser()
    config.read('/tmp/config.ini')
    print('Config File Parsed')

    s3_client = boto3.client('s3', region_name=config.get('aws', 'REGION_NAME'),
                             aws_access_key_id=config.get('aws', 'ACCESS_KEY'),
                             aws_secret_access_key=config.get('aws', 'SECRET_KEY'))
    comprehend = boto3.client("comprehend", region_name=config.get('aws', 'REGION_NAME'),
                              aws_access_key_id=config.get('aws', 'ACCESS_KEY'),
                              aws_secret_access_key=config.get('aws', 'SECRET_KEY'))

    reddit_stocks = s3_client.get_object(Bucket=bucket, Key=s3_key)
    df = pd.read_csv(reddit_stocks['Body'], sep=',')
    df.drop(df.columns[df.columns.str.contains('Unnamed', case=False)], axis=1, inplace=True)
    df.drop(df.columns[df.columns.str.contains('0', case=False)], axis=1, inplace=True)
    df.drop(df.columns[df.columns.str.contains('count', case=False)], axis=1, inplace=True)

    entity_dict = df.set_index('stock_symbol').T.to_dict('list')

    entity_title_dict = dict()

    for k, v in entity_dict.items():
        entity_title_dict[k] = list(str(entity_dict[k])[3:-3].replace("'", "").split(','))

    company_sentiment = dict()

    symbol = event["currentIntent"]["slots"]["Symbol"]

    if not symbol or (not symbol in entity_title_dict):
        output = "Invalid stock symbol"

    else:
        company_sentiment[symbol] = {'POSITIVE':0, 'NEGATIVE': 0, 'NEUTRAL': 0, 'MIXED': 0}
        for j in entity_title_dict[symbol]:
            sentiment = comprehend.detect_sentiment(Text = j, LanguageCode = "en")
            company_sentiment[symbol][sentiment['Sentiment']] = company_sentiment[symbol][sentiment['Sentiment']] + 1

        output = 'The sentiment of ' + str(symbol) + ': ' + str(company_sentiment[symbol]) + '.\n For real time prices of any stock, type "Ticker" in the chat box'

    result = {
        "sessionAttributes": {},
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
            "message": {
                "contentType": "PlainText",
                "content": output
            }
        }
    }

    return result
