import requests
event = {
    "Records":
}


url = 'http://localhost:8080/2015-03-31/functions/function/invocations'
response = requests.post(url,json=event)
print(response.json())