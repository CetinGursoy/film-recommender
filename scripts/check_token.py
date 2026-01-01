
import requests
import json
import base64

BASE_URL = "http://localhost:8000"
USERNAME = "testuser"
PASSWORD = "testpassword123"

def check_token():
    try:
        # Login
        print(f"Logging in...")
        res = requests.post(f"{BASE_URL}/auth/login", json={"email": "test@test.com", "password": PASSWORD})
        
        if res.status_code != 200:
             # Try register if login failed
            print("Login failed, trying registration...")
            res = requests.post(f"{BASE_URL}/auth/register", json={"username": USERNAME, "email": "test@test.com", "password": PASSWORD})
            if res.status_code != 200:
                 print(f"Register failed: {res.text}")
                 return
            # Login again
            res = requests.post(f"{BASE_URL}/auth/login", json={"email": "test@test.com", "password": PASSWORD})

        if res.status_code != 200:
            print(f"Login failed: {res.text}")
            return

        token = res.json()["access_token"]
        print("Login successful. Checking token...")
        
        # Decode payload (no signature check for this test)
        parts = token.split(".")
        if len(parts) < 2:
            print("Invalid token format")
            return
            
        payload_str = parts[1]
        # Pad base64
        payload_str += "=" * ((4 - len(payload_str) % 4) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_str))
        
        print("Token Payload:", payload)
        if "sub" in payload and payload["sub"] == USERNAME:
            print("SUCCESS: 'sub' claim is present and correct.")
        else:
            print(f"FAILURE: 'sub' claim missing or incorrect. Found: {payload.get('sub')}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_token()
