# Final Project - Stock Market Analysis Pipeline

[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)

#### Quick Links

[Project Presentation](https://codelabs-preview.appspot.com/?file_id=13Hv8gckEHooy4swCCXDuDKyrL-2J_BWyeBuB82hu1Zw#0) <br /> 
[Project Proposal](https://codelabs-preview.appspot.com/?file_id=1FS1VfRguDZWVQZ7R4a-onoPqQTNTHMEDZonDRoxTHsk#0) <br />
[Web Application](http://stock-website-team6.s3-website-us-east-1.amazonaws.com/) <br /> 
[Test Cases](https://codelabs-preview.appspot.com/?file_id=1-6XEDP7HqJkJHIFf83E6HPgncf_v23PfY46ktEMGPuw#0) <br />
[Docker image](https://hub.docker.com/r/nidhi2019/stock-analysis-lstm-model) <br /> 
[Demo](https://youtu.be/_fobmukXyj4)
---

## Project Structure
```
Final_Project/
├── architecture_diagram/
│   ├── Final_Project_architecture_diagram.png
│   └── Project_Proposal.png
├── aws_config/
│   ├── API_Gateway_role_with_policies.png
│   ├── Cognito_auth_role_with_policies.png
│   ├── Cognito_unauth_role_with_policies.png
│   ├── Lambda_role_with_policies.png
│   └── Lex_role_with_policies.png
├── config/
│   └── config.ini
├── lambda_batch_process/
│   ├── config.yaml
│   ├── pushing-files-s3.py
│   └── requirements.txt
├── lambda_files_for_dashboard/
│   ├── config.yaml
│   ├── requirements.txt
│   └── s3-trigger.py
├── lambda_reddit_news/
│   ├── config.yaml
│   ├── lambda_function.py
│   └── requirements.txt
├── lambda_reddit_sentiment/
│   ├── config.yaml
│   ├── lambda_function.py
│   └── requirements.txt
├── lambda_reddit_stock/
│   ├── config.yaml
│   ├── lambda_function.py
│   └── requirements.txt
├── lambda_stock_current/
│   ├── config.yaml
│   ├── lambda_function.py
│   └── requirements.txt
├── lambda_stock_prediction/
│   ├── config.yaml
│   ├── lambda_function.py
│   └── requirements.txt
├── LSTM_model/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── README.md
└── Static-Website-Deploy/
    ├── about.html
    ├── architecture.html
    ├── contact.html
    ├── css/
    │   ├── clean-blog.css
    │   └── clean-blog.min.css
    ├── dashboard.html
    ├── home.html
    ├── img/
    │   ├── img.jpeg
    │   └── project.png
    ├── index.html
    ├── register.html
    ├── script/
    │   ├── amazon-cognito-identity.min.js
    │   ├── amazon-cognito-identity.min.js.map
    │   ├── aws-cognito-sdk.min.js
    │   ├── aws-cognito-sdk.min.js.map
    │   ├── aws-sdk-2.487.0.min.js
    │   ├── jquery.min.js
    │   └── jquery.min.map
    └── vendor/
        ├── bootstrap/
        ├── fontawesome-free/
        └── jquery/
```
---
## Table of Contents

- [Introduction](#introduction)
- [Setup](#setup)
- [TestCases](#testcases)

---

## Introduction

Scalable Data Pipeline for collecting stock data from Reddit API and Yahoo Finance,
generating text entities(stock names) & sentiment analysis,
current stock prices, historical stock performance trend & stock forecast 
and deploying them on the cloud to run completely on a Serverless Infrastructure on-demand. 
Facilitated this service by creating interactive chatbot for user interaction using Amazon Lex and integrated into static website hosted on S3.
Stock forecast is done using `LSTM` model.

#### Architecture
![Screen Shot 2021-04-30 at 1 35 00 AM](https://user-images.githubusercontent.com/56357740/116652989-50084b80-a954-11eb-8b39-98be4455bb5b.png)
---
## Setup
### 1. AWS Setup
The pipeline requires an Amazon Web Services account to deploy and run. Signup for an AWS Account [here](https://portal.aws.amazon.com/billing/signup#/start). The pipeline uses the folllowing AWS Services:

- Lambda
- S3
- CloudWatch 
- Comprehend
- Amazon Lex

Create new roles on the AWS IAM Console by taking reference from images found at `aws_config/` on this repository to allow access to all required AWS Services.

### 2. Clone
Clone this repo to your local machine using `https://github.com/goyal07nidhi/Team6_CSYE7245_Spring2021.git`

### 3. `config.ini` Setup

All scripts make use of the `configparser` Python library to easily pass configuration data to running scripts/deployed packages. This allows for easy replication of code with zero modifications to Python scripts. Find configuration file can be found in `config/config.ini` directory on this repository. Modify the file with your environment variables and place it on your S3 bucket under the `config` directory like so `YourS3BucketName/config/config.ini` ; All packages and scripts are designed to read the configuration values from this path.

```
[aws]
ACCESS_KEY = <Enter your access key>
SECRET_KEY = <Enter your secret key>
BUCKET = <Enter your bucket name >
REGION_NAME = <Enter your region name >

[reddit]
CLIENT_ID = <Enter your reddit api client id >
CLIENT_SECRET_ID = <Enter your reddit api client secret id >
USERNAME = <Enter your reddit api username>
PASSWORD = <Enter your reddit api password>
```
### 4. Deploying Lambda Functions 

The pipeline uses AWS Lambda Functions for Serverless Computing. All directories on this repo marked with the prefix `lambda_` are Lambda functions that have to be deployed on AWS. All functions follow a common deployment process. 

#### Deploy serverless Python code in AWS Lambda

Python Lambda is toolkit to easily package and deploy serverless code to AWS Lambda. Packaging is requried since AWS Lambda functions only ship with basic Python libraries and do not contain external libraries. Any external libraries to be used will be have to be packaged into a `.zip` and deployed to AWS Lambda. More information about Python Lambda can be found [here](https://github.com/nficano/python-lambda)

#### Setup your `config.yaml`

All `lambda_` directories contain a `config.yaml` file with the configuration information required to deploy the Lambda package to AWS. Configure the file with your access keys, secret access keys and function name before packaging and deploying the Python code. An example is as follows

```
region: us-east-1

function_name: lambda_function
handler: service.handler
description: Deployed lambda Function
runtime: python3.7
role: <Enter the role name created earlier>

# if access key and secret are left blank, boto will use the credentials
# defined in the [default] section of ~/.aws/credentials.
aws_access_key_id: <Enter your Access Keys>
aws_secret_access_key: <Enter your Secret Access Keys>

timeout: 15
memory_size: 1024

environment_variables:
    ip_bucket: <enter_your_S3_Bucket>
    s3_key: <s3_file_key>

# Build options
build:
  source_directories: lib
```
Create a Virtual Environment and install all Python dependencies mentioned in requirements.txt.

#### Deploying the Lambda Function
Create a new Lambda function on your AWS Lambda Console.
For deploying lambda, zip the contents of the directory and upload the file to the Lambda console
and make the necessary changes like lambda handler name & function, the environment variables from the lambda console:

>Key:       Value <br />
ip_bucket: <enter_your_S3_Bucket> <br />
s3_key:    <s3_file_key> <br />

Trigger the lambda function by cloud watch scheduler for lambda_batch_process and lambda_files_for_dashboard functions.

Although - you can do this with python-lambda as well, but we are using the above method.

### 5. AWS Cognito Setup

1. Configuring User Pool
    - Go to AWS Cognito Service and create a user pool with defaults
    - Copy the generated ```pool-id```
    - Go to App Clients and click ```Add on app client```
    - Create an app client by giving ```App client name``` and uncheck the ```Generate client secret```. Note the App client id
2. Configure an Identity Pool
    - Go to AWS Cognito service and create identity pool by entering the ```Identity Pool name``` and expand ```Authenication providers``` select ```cognito``` tab and provide the ```User Pool ID``` and ```App client id``` generated in step 1
    - Note the IAM Roles created in the next ```Your Cognito identities require access to your resources``` page
    - After creating Identity Pool, go to edit Identity Pool and note the ```Identity pool ID```
3. Allow AWS Resource Access to Identity Pool Role
    - Go to IAM service and attach ```AmazonS3FullAccess``` policy to the IAM Roles created in Step 2

### 6. Amazon Lex Setup

- Sign in to the AWS Management Console and open the Amazon Lex console at [here](https://console.aws.amazon.com/lex/).
- On the Bots page, choose `Create` and provide the necessary information like IAM service for LexBots , and then choose `Create`.
- The console makes the necessary requests to Amazon Lex to save the configuration. Wait for confirmation that your bot was built.
- The console then displays the bot editor window, now you can create intent and test the bot.

#### Amazon Lex editor

- Sample utterances: Here we put input for the intent.
- Lambda initialization and validation: If intent require any lambda function to trigger the intent, we put the lambda function here:
eg, Lambda function: lambda_reddit_news <br/>
  Version or alias: Latest
- Slots: Here we can give event name for the intent. 
- Fulfillment: Here we have two options:
  1. AWS Lambda function - choose this option when we are creating lambda function for the intent response
  2. Return parameters to client - here we can directly assign responses  in the form of messages for the intent.
- After providing all above information, we save the intent and build the bot.

#### Amazon Lex Intent
1. Welcome_Intent
2. Choice_Input_Intent
3. Reddit_News_Intent
4. Reddit_Stock_Intent
5. Reddit_Sentiment_Intent
6. Stock_Info_Intent
7. Stock_Historical_Intent
8. Stock_Prediction_Intent
9. Bye_Intent

#### Amazon Lex Error Handling

We also implemented error handling for the chatbox.

- Clarification prompts:  If the chatbox couldn’t understand the user’s utterances, it will throw an error. <br/>
Error message: Sorry, can you please repeat that? 
  
- Hang-up phrase: If the chatbox couldn’t find the correct utterances by the user, it will throw an error. <br/>
Error message: Sorry, I could not understand. Goodbye.
  
#### Amazon Lex Deployment
After building the bot, we created alias name for bot and publish the bot. We are integrating this bot into our static website for interactive communication.

The pipeline requires six lambdas to run on AWS to facilitate value in Amazon Lex.

### 7. Webpage Deployment
- Create an S3 bucket
- In ```Set Permissions/Block all public access``` section and unselect the first 2 permissions
- Go to ```Properties``` section and enable ```Static website hosting```. Enter Index document as ```index.html```
- In ```Permissions``` tab, go to ```CORS configuration``` and paste the below code

```
[
    {
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "PUT",
            "POST",
            "DELETE",
            "GET"
        ],
        "AllowedOrigins": [
            "*"
        ],
        "ExposeHeaders": []
    }
]
```
- Upload all the files required to the bucket and make them public
- We can view the webpage using the end-point in ```Properties/Static website hosting```

## 8. Prediction Model (LSTM)
Time-series forecasting models are the models that are capable to predict future values based on previously observed values. Time-series forecasting is widely used for non-stationary data. Non-stationary data are called the data whose statistical properties e.g. the mean and standard deviation are not constant over time but instead, these metrics vary over time.

Long short-term memory (LSTM) is an artificial recurrent neural network (RNN) architecture used in the field of deep learning. LSTM models are able to store information over a period of time. This characteristic is extremely useful when we deal with Time-Series or Sequential Data. When using an LSTM model we are free and able to decide what information will be stored and what discarded. 

We are taking 5 years of data for multiple companies and applying the LSTM model on data and predicting the Stock price for the next 90 days. The results are stored in S3

## 9. Docker Image for prediction model
In this directory, we have `Dockerfile` under the LSTM_model directory, a blueprint for our development environment, and `requirements.txt` that lists the python dependencies.

#### Build:
##### Local
For using the model, follow these steps:
1. `git clone` this repo
2. `cd Final_Project/LSTM_model/`
3. `docker build -t nidhi2019/stock-analysis-lstm-model:latest .`

##### Dockerhub
`docker pull nidhi2019/stock-analysis-lstm-model`

#### Run
`docker run -it --rm -p 5000:5000 nidhi2019/stock-analysis-lstm-model`

## TestCases

All Test Cases have been documented [here](https://codelabs-preview.appspot.com/?file_id=1-6XEDP7HqJkJHIFf83E6HPgncf_v23PfY46ktEMGPuw#0)
 
Chatbot can be accessed using this web application: [Web Application](http://stock-website-team6.s3-website-us-east-1.amazonaws.com/)

**Team Members**<br />

Nidhi Goyal <br />
Kanika Damodarsingh Negi<br /> 
Rishvita Reddy Bhumireddy<br />

## Citation:
https://docs.aws.amazon.com/lexv2/latest/dg/lambda.html </br>
https://medium.com/@sumindaniro/user-authentication-and-authorization-with-aws-cognito-d204492dd1d0 </br>
https://docs.aws.amazon.com/lex/latest/dg/lambda-input-response-format.html </br>
https://docs.aws.amazon.com/comprehend/latest/dg/functionality.html </br>
https://github.com/nficano/python-lambda </br>
