import requests

url = "http://localhost:8000/api/ai/summary/stream"
data = {"url": "https://www.youtube.com/watch?v=33bZIOLX4do"}

try:
    response = requests.post(url, json=data, timeout=60, stream=True)
    print("Status:", response.status_code)
    
    count = 0
    for line in response.iter_lines():
        if count > 5:
            break
        if line:
            print("Line:", line.decode('utf-8')[:100])
            count += 1
except Exception as e:
    print("Error:", str(e))