
import requests
import json
import base64

BASE_URL = "http://localhost:8000"
USERNAME = "testuser"
PASSWORD = "testpassword123"

def check_my_reviews():
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
        headers = {"Authorization": f"Bearer {token}"}
        print("Login successful. Fetching my reviews...")
        
        res = requests.get(f"{BASE_URL}/reviews/my-reviews", headers=headers)
        if res.status_code == 200:
            print(f"Success! Reviews: {res.json()}")
        else:
            print(f"Failed: {res.status_code} - {res.text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_my_reviews()
