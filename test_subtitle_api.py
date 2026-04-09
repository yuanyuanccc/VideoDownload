import requests

url = "http://localhost:8000/api/ai/subtitle"
data = {"url": "https://www.bilibili.com/video/BV1uYAuzYEjX/"}

response = requests.post(url, json=data)
print("Status:", response.status_code)
print("Response:", response.json())