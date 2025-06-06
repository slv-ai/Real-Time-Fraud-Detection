import os
import json
import boto3
import base64
import mlflow

kinesis_client=boto3.client('kinesis')

PREDICTIONS_STREAM_NAME=os.getenv("PREDICTIONS_STREAM_NAME",'fraud_detections')

RUN_ID=os.getenv("RUN_ID")

logged_model=f's3://mlflow-fraud-detection-slv/1/{RUN_ID}/artifacts/model'
model=mlflow.pyfunc.load_model(logged_model)

TEST_RUN=os.getenv('TEST_RUN','False') == 'True'

def preprocess_features(df):
    cat_cols=df.select_dtypes(include=['object', 'category']).columns
    for col in cat_cols:
        df[col]=df[col].fillna('Unknown').astype(str)
        #fit label encoder
        le=LabelEncoder()
        df[col]=le.fit_transform(df[col])
        
    return df

def predict(features):
    pred=model.predict(features)
    return pred[0]

def lambda_handler(event,context):

    predicions_events =[]

    for record in event['Records']:
        encoded_data=record['kinesis']['data']
        decoded_data=base64.b64decode(encoded_data).decode('utf-8')

        record_data = json.loads(decoded_data)
        TransactionID = record_data['TransactionID']

        features = preprocess_features(record_data)
        prediction=predict(features)

        prediction_event ={
            'model':'Fraud-detection-model',
            'version' : '123',
            'prediction': {
                'isFraud': prediction,
                'TransactionID': TransactionID
            }
        }

        if not TEST_RUN:
            kinesis_client.put_record(
                Stream_name=PREDICTIONS_STREAM_NAME,
                data = json.dumps(prediction_event),
                partition_key = TransactionID
            )

        predicions_events.append(predicions_event)

    return{
        'predictions':predicions_events
    }


