import os
import json
import boto3
import base64
import mlflow



def get_model_location(run_id):
    model_location=os.getenv('MODEL_LOCATION')
    if not None:
        return model_location
    model_bucket = os.getenv('S3_BUCKET_NAME','mlflow-fraud-detection-slv')
    experiment_id = os.getenv('MLFLOW_EXPERIMENT_ID','1')

    model_location=f's3://{model_bucket}/{experiment_id}/{RUN_ID}/artifacts/model'

    return model_location

def load_model(run_id):
    model_path=get_model_location(run_id)
    model=mlflow.pfunc.load_model(model_path)
    return model


def base64_decode(encoded_data):
    decoded_data=base64.b64decode(encoded_data).decode('utf-8')
    record_data = json.loads(decoded_data)
    return record_data

class ModelService:
    def __init__(self,model,model_version=None,callbacks=None):
        self.model=model
        self.model_version=model_version
        self.callbacks=callbacks or []

    def preprocess_features(self,fraud_Data):
        cat_cols=fraud_Data.select_dtypes(include=['object', 'category']).columns
        for col in cat_cols:
            fraud_Data[col]=fraud_Data[col].fillna('Unknown').astype(str)
            #fit label encoder
            le=LabelEncoder()
            fraud_Data[col]=le.fit_transform(fraud_Data[col])
        return fraud_Data


    def predict(self,features):
        pred=model.predict(features)
        return pred[0]

    def lambda_handler(self,event):

        predicions_events =[]

        for record in event['Records']:
            encoded_data=record['kinesis']['data']
            record_data = base64_decode(encoded_data)
            print(record_data)
            TransactionID = record_data['TransactionID']

            features = self.preprocess_features(record_data)
            prediction=self.predict(features)

            prediction_event ={
                'model':'Fraud-detection-model',
                'version' : self.model_version,
                'prediction': {
                    'isFraud': prediction,
                    'TransactionID': TransactionID
                    }
            }
            for callback in self.callbacks:
                callback(predicion_event)
            predicions_events.append(predicion_event)

        return {'predictions': predicions_events}

class KinesisCallback:

    def __init__(self,kinesis_client,prediction_stream_name):
        self.kinesis_client=kinesis_client,
        self.prediction_stream_name=prediction_stream_name

    def put_record(self,predicion_event):
        TransactionID=predicion_event['prediction']['TransactionID']

        self.kinesis_client.put_record(
            Stream_name=prediction_stream_name,
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





        










      
    