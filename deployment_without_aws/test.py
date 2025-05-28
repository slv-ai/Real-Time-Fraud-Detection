import requests
data = {

}

url='http://localhost:9696/predict'
response=requests.post(url,json=data)
print(response.json())