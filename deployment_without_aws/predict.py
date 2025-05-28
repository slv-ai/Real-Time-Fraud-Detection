import os
import mlflow
from flask import Flask,request,jsonify

RUN_ID =
logged_model = f's3://fraud_detection_models/1/{RUN_ID}/artifacts/model'
model=mlflow.pyfunc.load_model(logged_model)

def predict(data):
    preds=model.predict(data)
    return float(preds[0])

app=Flask("fraud-detection")
 
@app.route('./predict',methods=['POST'])
def predict_Endpoint():
    data=requests.get_json()
    pred=predict(data)

    result = {
        'isFraud' : pred,
        'modelversion' : RUN_ID
    } 

    return jsonify(result)


if __name__ == "main":
    app.run(debug=True,host='0.0.0.0',port=9696)