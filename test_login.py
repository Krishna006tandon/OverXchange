import requests
import json

# Test login API
url = "http://localhost:5000/api/login"
data = {
    "username": "rajesh@freshfoods.com",
    "password": "password123"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}") 