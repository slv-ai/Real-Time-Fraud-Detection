# Real-Time-Fraud-Detection
```

mlflow server \
  --host 0.0.0.0 \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root s3://mlflow-fraud-detection-slv/

  pydantic=1.10.8
  mlflow=2.2.2
  scikit-learn=1.0.2
  
pipenv install boto3 mlflow==2.2.2 scikit-learn==1.0.2 pydantic==1.10.8 --python=3.9