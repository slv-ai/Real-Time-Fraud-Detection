import base64
import json
with open('test_data.json','r') as f:
  data = json.load(f)
data_json = json.dumps(data)
data_b64 = base64.b64encode(data_json.encode('utf-8')).decode('utf-8')
print(data_b64)
with open('data.b64','w',encoding='utf-8') as f_out:
  f_out.write(data_b64)