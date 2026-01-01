
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
USERNAME = "testuser"
PASSWORD = "testpassword123"
MOVIE_ID = 140 # Inception or any existing movie

def test_deletion():
    # 1. Register/Login to get token
    session = requests.Session()
    
    # Try login first
    print(f"Logging in as {USERNAME}...")
    try:
        # Try login first
        # Auth.py uses data.email, so we must provide email.
        res = session.post(f"{BASE_URL}/auth/login", json={"email": "test@test.com", "password": PASSWORD})
        if res.status_code != 200:
            # Try register
            print("Login failed, trying registration...")
            res = session.post(f"{BASE_URL}/auth/register", json={"username": USERNAME, "email": "test@test.com", "password": PASSWORD})
            if res.status_code != 200:
                print(f"Registration failed: {res.text}")
                return
            # Login again
            res = session.post(f"{BASE_URL}/auth/login", json={"email": "test@test.com", "password": PASSWORD})
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    if res.status_code != 200:
        print(f"Login failed: {res.text}")
        return

    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful.")

    # 2. Add a comment
    print("Adding a comment...")
    comment_text = "This is a test comment to delete."
    res = session.post(f"{BASE_URL}/reviews/add/{MOVIE_ID}?text={comment_text}&is_spoiler=false", headers=headers)
    if res.status_code != 200:
        print(f"Add comment failed: {res.text}")
        return
    
    review_data = res.json().get("review")
    if not review_data:
        # Fallback if structure is different
        print("Review created but response format unexpected.")
        # Fetch reviews to find it
        res = session.get(f"{BASE_URL}/reviews/{MOVIE_ID}")
        reviews = res.json()
        my_reviews = [r for r in reviews if r['user']['username'] == USERNAME]
        if not my_reviews:
            print("Could not find created review.")
            return
        review_id = my_reviews[0]['id']
    else:
        review_id = review_data['id']
    
    print(f"Comment added with ID: {review_id}")

    # 3. Delete the comment
    print(f"Deleting comment {review_id}...")
    res = session.delete(f"{BASE_URL}/reviews/delete/{review_id}", headers=headers)
    
    if res.status_code == 200:
        print("Deletion successful!")
    else:
        print(f"Deletion failed: {res.status_code} - {res.text}")

    # 4. Verify deletion
    res = session.get(f"{BASE_URL}/reviews/{MOVIE_ID}")
    reviews = res.json()
    found = any(r['id'] == review_id for r in reviews)
    if not found:
        print("Verification passed: Comment is gone.")
    else:
        print("Verification failed: Comment is still there.")

if __name__ == "__main__":
    test_deletion()
