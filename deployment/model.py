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



def get_model_location(run_id):
    model_location=os.getenv('MODEL_LOCATION')
    if model_location is  not None:
        return model_location
    model_bucket = os.getenv('S3_BUCKET_NAME','mlflow-fraud-detection-slv')
    experiment_id = os.getenv('MLFLOW_EXPERIMENT_ID','1')

    model_location=f's3://{model_bucket}/{experiment_id}/{run_id}/artifacts/model'

    return model_location

def load_model(run_id):
    model_path=get_model_location(run_id)
    model=mlflow.pyfunc.load_model(model_path)
    return model

def load_label_encoders():
    MODEL_BUCKET = os.getenv('S3_BUCKET_NAME','mlflow-fraud-detection-slv')
    obj = s3.get_object(Bucket=MODEL_BUCKET, Key='encoders/label_encoders.pkl')
    encoders=joblib.load(BytesIO(obj['Body'].read()))
    #print("Loaded encoders:", list(encoders.keys()))
    return encoders


def base64_decode(encoded_data):
    decoded_data=base64.b64decode(encoded_data).decode('utf-8')
    record_data = json.loads(decoded_data)
    return record_data

class ModelService:
    def __init__(self,model,encoders,model_version=None,callbacks=None):
        self.model=model
        self.encoders = encoders
        self.model_version=model_version
        self.callbacks=callbacks or []

    def preprocess_features(self,df, cat_cols):
        missing_cols = []

        for col in cat_cols:
            df[col] = df[col].fillna('Unknown').astype(str)
            le = self.encoders.get(col)

            if le:
                df[col] = le.transform(df[col])
            else:
                df[col] = -1
                missing_cols.append(col)

        if missing_cols:
            logger.warning(f"No label encoder found for columns: {missing_cols}. Filling with -1")

        return df



    def predict(self,features):
        pred=self.model.predict(features)
        return pred[0]

    def lambda_handler(self,event):

        predictions_events =[]

        for record in event['Records']:
            encoded_data=record['kinesis']['data']
            record_data = base64_decode(encoded_data)
            print(record_data)
            TransactionID = record_data.get('TransactionID', 'unknown')

            #convert dict into dataframe
            features_df=pd.DataFrame([record_data])

            #replace null with np.nan
            features_df=features_df.where(pd.notnull(features_df), np.nan)
            #preprocess features & predict
            cat_cols=['ProductCD', 'card4', 'card6', 'P_emaildomain', 'R_emaildomain', 'M1',
            'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'id_12', 'id_15',
            'id_16', 'id_28', 'id_29', 'id_30', 'id_31', 'id_33', 'id_34', 'id_35',
            'id_36', 'id_37', 'id_38', 'DeviceType', 'DeviceInfo']
            features = self.preprocess_features(features_df,cat_cols)
            prediction=self.predict(features)

            prediction_event ={
                'model':'Fraud-detection-model',
                'version' : self.model_version,
                'prediction': {
                    'isFraud': int(prediction),
                    'TransactionID': TransactionID
                    }
            }
            for callback in self.callbacks:
                callback(prediction_event)
            predictions_events.append(prediction_event)

        return {'predictions': predictions_events}

class KinesisCallback:

    def __init__(self,kinesis_client,prediction_stream_name):
        self.kinesis_client=kinesis_client
        self.prediction_stream_name=prediction_stream_name

    def put_record(self,predicion_event):
        TransactionID=predicion_event['prediction']['TransactionID']

        self.kinesis_client.put_record(
            Stream_name=self.prediction_stream_name,
            data = json.dumps(prediction_event),
            partition_key = TransactionID
        )


def create_kinesis_client():
    endpoint_url = os.getenv("KINESIS_ENDPOINT_URL")
    if endpoint_url is None:
        return boto3.client("kinesis")
    return boto3.client('kinesis',endpoint_url=endpoint_url)

def init(prediction_stream_name:str,run_id=str,test_run=bool):
    model=load_model(run_id)
    callbacks=[]
    if not test_run:
        kinesis_client=create_kinesis_client()
        kinesis_callback=KinesisCallback(kinesis_client,prediction_stream_name)
        callbacks.append(kinesis_callback.put_record)
    model_service=ModelService(model=model,model_version=run_id,callbacks=callbacks)

    return model_service





        










      
    