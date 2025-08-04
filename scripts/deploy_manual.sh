AWS_REGION="us-east-1"
export MODEL_BUCKET_PROD="prod_input_transactions-mlflow-models"
export PREDICTIONS_STREAM_NAME="prod_fraud_predictions"
export LAMBDA_FUNCTION="prod_fraud_transaction_prediction_lambda"

export MODEL_BUCKET_DEV="mlflow-models-slv"

export RUN_ID=$(aws s3api list-objects-v2 --bucket ${MODEL_BUCKET_DEV} \
--query 'sort_by(Contents, &LastModified)[-1].Key' --output=text | cut -f2 -d/)

aws s3 sync s3://${MODEL_BUCKET_DEV} s3://${MODEL_BUCKET_PROD}

variables="{PREDICTIONS_STREAM_NAME=${PREDICTIONS_STREAM_NAME}, MODEL_BUCKET=${MODEL_BUCKET_PROD}, RUN_ID=${RUN_ID}}"

aws lambda update-function-configuration --function-name ${LAMBDA_FUNCTION} --environment "Variables=${variables}"