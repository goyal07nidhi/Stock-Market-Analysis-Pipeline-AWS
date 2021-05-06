import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
import tensorflow as tf
import boto3
from io import StringIO

ACCESS_KEY = "aws-access-key"
SECRET_KEY = "aws-secret-access-key"
BUCKET = 'aws-bucket'
REGION_NAME = 'aws-region'

# To print all filenames in a certain directory in a bucket
s3 = boto3.client('s3', region_name=REGION_NAME, aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

filename = []

# Get a list of keys in an S3 bucket.
resp = s3.list_objects_v2(Bucket=BUCKET, Prefix='Batchprocess')
for obj in resp['Contents']:
    files = obj['Key']
    filename.append(files)

for x in filename:
    try:
        if x.split('/')[1] != '':
            history = s3.get_object(Bucket=BUCKET, Key=x)
            df = pd.read_csv(history['Body'], sep=',')

            # considering Close column
            df1 = df.reset_index()['Close']

            # Scaling the feartures
            scaler = MinMaxScaler(feature_range=(0, 1))
            df1 = scaler.fit_transform(np.array(df1).reshape(-1, 1))

            # splitting dataset into train and test split
            training_size = int(len(df1) * 0.65)
            test_size = len(df1) - training_size
            train_data, test_data = df1[0:training_size, :], df1[training_size:len(df1), :1]

            # convert an array of values into a dataset matrix
            def create_dataset(dataset, time_step=1):
                dataX, dataY = [], []
                for i in range(len(dataset) - time_step - 1):
                    a = dataset[i:(i + time_step), 0]
                    dataX.append(a)
                    dataY.append(dataset[i + time_step, 0])
                return np.array(dataX), np.array(dataY)


            # reshape into X=t,t+1,t+2,t+3 and Y=t+4
            time_step = 40
            X_train, y_train = create_dataset(train_data, time_step)
            X_test, ytest = create_dataset(test_data, time_step)

            print(test_size)

            # reshape input to be [samples, time steps, features] which is required for LSTM
            X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
            X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

            # Model
            model = Sequential()
            model.add(LSTM(50, return_sequences=True, input_shape=(40, 1)))
            model.add(LSTM(50, return_sequences=True))
            model.add(LSTM(50))
            model.add(Dense(1))
            model.compile(loss='mean_squared_error', optimizer='adam')

            # Fitting the data
            model.fit(X_train, y_train, validation_data=(X_test, ytest), epochs=100, batch_size=64, verbose=1)

            # Prediction for next 90 days
            x_input = test_data[len(test_data) - 40:].reshape(1, -1)

            temp_input = list(x_input)
            temp_input = temp_input[0].tolist()

            lst_output = []
            n_steps = 40
            i = 0

            while i < 90:
                if len(temp_input) > 40:
                    x_input = np.array(temp_input[1:])
                    x_input = x_input.reshape(1, -1)
                    x_input = x_input.reshape((1, n_steps, 1))
                    yhat = model.predict(x_input, verbose=0)
                    temp_input.extend(yhat[0].tolist())
                    temp_input = temp_input[1:]
                    lst_output.extend(yhat.tolist())
                    i = i + 1
                else:
                    x_input = x_input.reshape((1, n_steps, 1))
                    yhat = model.predict(x_input, verbose=0)
                    temp_input.extend(yhat[0].tolist())
                    lst_output.extend(yhat.tolist())
                    i = i + 1

            datelist = pd.date_range(pd.to_datetime(df['Date']).dt.date.max(), periods=90).tolist()

            predict_df = pd.DataFrame()
            predict_df['Date'] = datelist
            predict_df['Close_Price_Prediction'] = scaler.inverse_transform(lst_output)

            csv_buffer = StringIO()
            predict_df.to_csv(csv_buffer)
            s3_resource = boto3.resource('s3', region_name=REGION_NAME, aws_access_key_id='aws-access-key',
                                         aws_secret_access_key='aws-secret-access-key')
            s3_resource.Object('aws-bucket', 'prediction/' + x.split('/')[1]).put(Body=csv_buffer.getvalue())
    except:
        pass
