import pandas as pd
import boto3
import os
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')
print('Config File Parsed')


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

    s3 = boto3.client('s3', region_name=config.get('aws', 'REGION_NAME'),
                      aws_access_key_id=config.get('aws', 'ACCESS_KEY'),
                      aws_secret_access_key=config.get('aws', 'SECRET_KEY'))

    company = event["currentIntent"]["slots"]["Company"]
    date = event["currentIntent"]["slots"]["Date"]

    try:
        data = s3.get_object(Bucket=bucket, Key=s3_key)
        df = pd.read_csv(data['Body'], sep=',')

        predict = df[df['Date'] == date]['Close_Price_Prediction']

        output = "$" + str(round(predict.iloc[0], 2))

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
    except:
        result = {
            "sessionAttributes": {},
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                    "contentType": "PlainText",
                    "content": "Please choose date within 80days."
                }
            }
        }
        return result


