import requests
import json

url = "http://localhost:8000/api/ai/summary/stream"
data = {"url": "https://www.bilibili.com/video/BV1uYAuzYEjX/"}

response = requests.post(url, json=data, stream=True, headers={"Content-Type": "application/json"})
print("Status:", response.status_code)
print("Headers:", response.headers.get('content-type'))

if response.status_code == 200:
    for line in response.iter_lines():
        if line:
            print(line.decode('utf-8'))
            break
else:
    print("Error:", response.text[:500])