
import requests

try:
    print("Checking server health...")
    res = requests.get("http://localhost:8000/docs", timeout=5)
    print(f"Status: {res.status_code}")
except Exception as e:
    print(f"Error: {e}")
