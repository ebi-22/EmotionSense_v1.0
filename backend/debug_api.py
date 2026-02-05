
import requests
import json
import time

url = "http://localhost:5000/suggest"
payload = {
    "text": "ena pandra?",
    "context": "personal_chat",
    "tone": "caring"
}

print(f"Sending request to {url}...")
print(f"Payload: {payload}")

try:
    start = time.time()
    response = requests.post(url, json=payload, timeout=10)
    end = time.time()
    
    print(f"Status Code: {response.status_code}")
    print(f"Time Taken: {end - start:.2f}s")
    
    if response.status_code == 200:
        print("Success!")
        print(json.dumps(response.json(), indent=2))
    else:
        print("Error Response:")
        print(response.text)
        
except Exception as e:
    print(f"Request Failed: {e}")
