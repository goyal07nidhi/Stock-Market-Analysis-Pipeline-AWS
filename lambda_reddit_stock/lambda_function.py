from io import StringIO
import os
import boto3
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

    reddit_data = s3_client.get_object(Bucket=bucket, Key=s3_key)

    df = pd.read_csv(reddit_data['Body'], sep=',')
    headlines = list(df['title'])
    entity_list = []
    half = len(headlines) // 2
    list_1 = headlines[:half]
    list_2 = headlines[half:]
    sentence1 = ' '.join(list_1)
    sentence2 = ' '.join(list_2)

    entities1 = comprehend.detect_entities(Text=sentence1, LanguageCode="en")
    entities2 = comprehend.detect_entities(Text=sentence2, LanguageCode="en")
    for e in entities1['Entities']:
        try:
            if e['Type'] == 'ORGANIZATION':
                entity_list.append(e['Text'])
        except:
            pass
    for e in entities2['Entities']:
        try:
            if e['Type'] == 'ORGANIZATION':
                entity_list.append(e['Text'])
        except:
            pass

    entity_list = set(entity_list)
    entity_list = [e.upper() for e in entity_list]

    company_list = s3_client.get_object(Bucket=bucket, Key='reddit/CompanyList.csv')

    company_df = pd.read_csv(company_list['Body'], sep=',')

    company_df.drop(company_df.columns[company_df.columns.str.contains('Unnamed', case=False)], axis=1, inplace=True)

    stock_df = company_df[(company_df['stock_symbol'].isin(entity_list)) | (company_df['company'].isin(entity_list))][
        'stock_symbol']

    entity_title_dict = dict()
    for entity in stock_df:
        for headline in headlines:
            if entity in headline:
                if entity in entity_title_dict:
                    entity_title_dict[entity].append(headline)
                else:
                    entity_title_dict[entity] = [headline]

    stock_count = []

    for key, value in entity_title_dict.items():
        stock_count.append((key, len(value), value))
    stock_count.sort(key=lambda x: -x[1])
    entity_df = DataFrame(stock_count, columns=['stock_symbol', 'count', 'headlines'])

    top5 = entity_df.nlargest(5, ['count'])

    print("Loading data to S3..")
    # load the dataframe as .csv file to S3
    csv_buffer = StringIO()
    top5.to_csv(csv_buffer)
    s3_resource = boto3.resource('s3', region_name=config.get('aws', 'REGION_NAME'), aws_access_key_id=config.get('aws', 'ACCESS_KEY'), aws_secret_access_key=config.get('aws', 'SECRET_KEY'))

    s3_resource.Object(bucket, 'reddit/redditstock.csv').put(Body=csv_buffer.getvalue())

    print("Successful")

    output = 'Redditors are talking about these Stocks: ' + str(list(top5['stock_symbol'])) + ' If you would like to know about the sentiments of the discussions, write "Sentiment" in the chatbox.'

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
