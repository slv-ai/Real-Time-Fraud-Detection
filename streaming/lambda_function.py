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
PREDICTIONS_STREAM_NAME=os.getenv("PREDICTIONS_STREAM_NAME",'fraud-detections')
RUN_ID=os.getenv("RUN_ID","522ab897b0564d749772ef0db9629070")
MODEL_BUCKET = os.getenv("MODEL_BUCKET",'mlflow-fraud-detection-slv')
TEST_RUN=os.getenv('TEST_RUN','False') == 'True'

#load model
logged_model=f's3://mlflow-fraud-detection-slv/1/{RUN_ID}/artifacts/model'
model=mlflow.pyfunc.load_model(logged_model)

# load label encoders
def load_label_encoders():
    obj = s3.get_object(Bucket=MODEL_BUCKET, Key='encoders/label_encoders.pkl')
    encoders=joblib.load(BytesIO(obj['Body'].read()))
    #print("Loaded encoders:", list(encoders.keys()))
    return encoders


def preprocess_features(df, label_encoders, cat_cols):
    missing_cols = []

    for col in cat_cols:
        df[col] = df[col].fillna('Unknown').astype(str)
        le = label_encoders.get(col)

        if le:
            df[col] = le.transform(df[col])
        else:
            df[col] = -1
            missing_cols.append(col)

    if missing_cols:
        logger.warning(f"No label encoder found for columns: {missing_cols}. Filling with -1")

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
        cat_cols=['ProductCD', 'card4', 'card6', 'P_emaildomain', 'R_emaildomain', 'M1',
       'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'id_12', 'id_15',
       'id_16', 'id_28', 'id_29', 'id_30', 'id_31', 'id_33', 'id_34', 'id_35',
       'id_36', 'id_37', 'id_38', 'DeviceType', 'DeviceInfo']
        features_df = preprocess_features(features_df,label_encoders,cat_cols)

        for col in features_df.columns:
            if features_df[col].dtype == 'object':
                features_df[col] = pd.to_numeric(features_df[col], errors='coerce')
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
                PartitionKey = str(TransactionID)
            )

        prediction_events.append(prediction_event)

    return{
        'predictions':prediction_events
    }


