import requests

try:
    response = requests.get("http://localhost:8000/config")
    print("Server Config:")
    print(response.json())
except Exception as e:
    print(f"Error calling server: {e}")
