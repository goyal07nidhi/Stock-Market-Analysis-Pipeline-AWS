import io
import os
import boto3
import yfinance as yf
import pandas as pd
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

    ticker = event["currentIntent"]["slots"]["Ticker"]

    company_list = s3_client.get_object(Bucket=bucket, Key=s3_key)
    company_df = pd.read_csv(company_list['Body'], sep=',')

    if ticker in list(company_df['stock_symbol']):
        data = yf.download(tickers=ticker, period='1d', interval='1m')
        # Real time data
        realtimePrice = data.iloc[-1:]
        output = 'Open:' + str(round(realtimePrice.iloc[0]['Open'], 2)) + ', ' + \
                 'Close:' + str(round(realtimePrice.iloc[0]['Close'], 2)) + ', ' + \
                 'High:' + str(round(realtimePrice.iloc[0]['High'], 2)) + ', ' + \
                 'Low:' + str(round(realtimePrice.iloc[0]['Low'], 2)) + ', ' + \
                 'Volume:' + str(round(realtimePrice.iloc[0]['Volume'], 2)) + ', ' + \
                 'Adj:' + str(round(realtimePrice.iloc[0]['Adj Close'], 2)) + ', '
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
    else :
        result = {
            "sessionAttributes": {},
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                    "contentType": "PlainText",
                    "content": "Please enter the correct symbol"
                }
            }
        }
        return result