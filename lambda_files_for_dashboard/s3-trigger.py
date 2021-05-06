import os
import pandas as pd
import numpy as np
import boto3
import s3fs
from configparser import ConfigParser


def main(event= None, context=None):

    bucket = os.environ['ip_bucket']
    s3_key = os.environ['s3_key']
    s3 = boto3.resource('s3')

    # Download Config File
    s3.Bucket(bucket).download_file('config/config.ini', '/tmp/config.ini')
    print('Config File Downloaded')

    config = ConfigParser()
    config.read('/tmp/config.ini')
    print('Config File Parsed')

    conn = boto3.client('s3', region_name=config.get('aws', 'REGION_NAME'),
                             aws_access_key_id=config.get('aws', 'ACCESS_KEY'),
                             aws_secret_access_key=config.get('aws', 'SECRET_KEY'))

    s3 = boto3.resource('s3')

    response = conn.list_objects(Bucket="historical-batchprocess")

    df_list = []
    itr = 0
    for file in response["Contents"]:

        obj = conn.get_object(Bucket="historical-batchprocess", Key=file["Key"])

        df_obj = pd.read_csv(obj["Body"])
        df_obj['Name'] = str(file["Key"])[:-4]

        df_list.append(df_obj)
        itr += 1

        if itr == 18:
            break
    df = pd.concat(df_list)
    df = df.dropna(axis=1, how='all')
    print(df.info())
    print(df.shape)
    fs =s3fs.S3FileSystem(key=config.get('aws', 'ACCESS_KEY'), secret=config.get('aws', 'SECRET_KEY'))
    with fs.open('team6-finalproject/s3-trigger/' + 'combined_results_after_scrapping.csv', 'w') as f:
        df.to_csv(f)


