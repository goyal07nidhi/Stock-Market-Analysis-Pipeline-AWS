from datetime import date
from dateutil.relativedelta import relativedelta
import time
import boto3
import pandas as pd
import s3fs
import yfinance as yf
import os
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

    s3_client = boto3.client('s3', region_name=config.get('aws', 'REGION_NAME'),
                             aws_access_key_id=config.get('aws', 'ACCESS_KEY'),
                             aws_secret_access_key=config.get('aws', 'SECRET_KEY'))
    start = date.today() + relativedelta(months=-60)

    end = date.today() + relativedelta(days=-3)
    company_list = s3_client.get_object(Bucket='team6-finalproject', Key='CompanyList.csv')
    company_df = pd.read_csv(company_list['Body'], sep=',')

    for i in company_df['stock_symbol']:
        data = yf.download(i, start=start, end=end)
        df = pd.DataFrame(data)
        fs = s3fs.S3FileSystem(key=config.get('aws', 'ACCESS_KEY'), secret=config.get('aws', 'SECRET_KEY'))
        with fs.open('s3://historical-batchprocess/' + i + '.csv', 'w') as f:
            df.to_csv(f)
        # Print data
        print(i)
        time.sleep(10)
