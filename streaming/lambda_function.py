import os
import json
import boto3
import base64
import mlflow
import joblib
from io import BytesIO
import pandas as pd
import numpy as np
import logging

#setup logging
logger=logging.getLogger()
logger.setLevel(logging.INFO)

#boto3 clients
kinesis_client=boto3.client('kinesis')
s3 = boto3.client('s3')

#environment variables
PREDICTIONS_STREAM_NAME=os.getenv("PREDICTIONS_STREAM_NAME",'fraud_detections')
RUN_ID=os.getenv("RUN_ID")
MODEL_BUCKET = os.getenv("MODEL_BUCKET",'mlflow-fraud-detection-slv')
TEST_RUN=os.getenv('TEST_RUN','False') == 'True'

#load model
logged_model=f's3://mlflow-fraud-detection-slv/1/{RUN_ID}/artifacts/model'
model=mlflow.pyfunc.load_model(logged_model)

# load label encoders
def load_label_encoders():
    obj = s3.get_object(Bucket=MODEL_BUCKET, Key='models/label_encoders.pkl')
    return joblib.load(BytesIO(obj['Body'].read()))


def preprocess_features(df,label_encoders):
    cat_cols=df.select_dtypes(include=['object', 'category']).columns
    for col in cat_cols:
        df[col]=df[col].fillna('Unknown').astype(str)
        #use prefitted laebl encoder
        le=label_encoders.get(col)
        if le:
            df[col]=le.transform(df[col])
        else :
            logger.warning(f"No label encoder found for column: {col}, defaulting to 0")
            df[col]=0       
        
    return df

def predict(features):
    pred=model.predict(features)
    return pred[0]

def lambda_handler(event,context):
    prediction_events =[]
    

    for record in event['Records']:
        encoded_data=record['kinesis']['data']
        decoded_data=base64.b64decode(encoded_data).decode('utf-8')

        record_data = json.loads(decoded_data)
        TransactionID = record_data.get('TransactionID', 'unknown')
        #TransactionID = record_data['TransactionID']
        
        #convert dict into dataframe
        features_df=pd.DataFrame([record_data])

        #replace null with np.nan
        features_df=features_df.where(pd.notnull(features_df), np.nan)
        #load encoders
        label_encoders = load_label_encoders()
        #preprocess features & predict
        features_df = preprocess_features(features_df,label_encoders)
        prediction=predict(features_df)

        prediction_event ={
            'model':'Fraud-detection-model',
            'version' : '123',
            'prediction': {
                'isFraud': int(prediction),
                'TransactionID': TransactionID
            }
        }

        if not TEST_RUN:
            kinesis_client.put_record(
                StreamName=PREDICTIONS_STREAM_NAME,
                Data = json.dumps(prediction_event),
                partition_key = str(TransactionID)
            )

        prediction_events.append(prediction_event)

    return{
        'predictions':prediction_events
    }


