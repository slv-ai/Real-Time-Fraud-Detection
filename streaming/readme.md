
```

mlflow server \
  --host 0.0.0.0 \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root s3://mlflow-fraud-detection-slv/

  pydantic=1.10.8
  mlflow=2.2.2
  scikit-learn=1.0.2
```
```
pipenv install boto3 mlflow==2.2.2 scikit-learn==1.0.2 pydantic==1.10.8 --python=3.9
```
```
KINESIS_STREAM_INPUT=input-transactions
aws kinesis put-record \
  --stream-name "$KINESIS_STREAM_INPUT" \
  --partition-key "1" \
  --data "$(base64 -w 0 /home/ubuntu/Real-Time-Fraud-Detection/test_data/test_data.json)"
```
````
export PREDICTIONS_STREAM_NAME="fraud-detections"
export RUN_ID="522ab897b0564d749772ef0db9629070"
export TEST_RUN="True"
``````
# to test output stream
KINESIS_STREAM_OUTPUT='fraud-detections'
SHARD='shardId-000000000000'

SHARD_ITERATOR=$(aws kinesis \
    get-shard-iterator \
        --shard-id ${SHARD} \
        --shard-iterator-type TRIM_HORIZON \
        --stream-name ${KINESIS_STREAM_OUTPUT} \
        --query 'ShardIterator' \
)

RESULT=$(aws kinesis get-records --shard-iterator $SHARD_ITERATOR)
echo $RESULT
echo ${RESULT} | jq -r '.Records[0].Data' | base64 --decode


# to get records to test locally
```
aws kinesis describe-stream --stream-name input-transactions --query "StreamDescription.Shards[*].ShardId" --output text
````
````
SHARD_ITERATOR=$(aws kinesis get-shard-iterator \
  --stream-name input-transactions \
  --shard-id shardId-000000000000 \
  --shard-iterator-type TRIM_HORIZON \
  --query 'ShardIterator' \
  --output text)
````
aws kinesis get-records --shard-iterator "$SHARD_ITERATOR" --limit 1 > input_records.json
````
````
cat input_records.json

`````

````
docker build -t fraud-detection-model-duration:v1 .

`````
`````
docker run -it --rm \
-p 8080:8080 \
-e PREDICTIONS_STREAM_NAME="fraud-detections" \
-e RUN_ID="522ab897b0564d749772ef0db9629070" \
-e TEST_RUN="True" \
-e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
-e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
-e AWS_DEFAULT_REGION="us-east-1" \
fraud-detection-model-duration:v1


docker run -it --rm \
-p 8080:8080 \
-e PREDICTIONS_STREAM_NAME="fraud-detections" \
-e RUN_ID="522ab897b0564d749772ef0db9629070" \
-e TEST_RUN="True" \
fraud-detection-model-duration:v1


python3 -m venv ~/.venvs/myenv
source ~/.venvs/myenv/bin/activate
