import requests
import json

URL = "http://localhost:8000/chatbot/ask"

QUERIES = [
    "Komedi",
    "Cem Yılmaz",
    "Beni ağlatan bir film öner",
    "Nasılsın",
    "Harry Potter",
    "Aksiyon filmleri",
    "Rastgele film"
]

def test_chatbot():
    print(f"Testing Chatbot at {URL}...\n")
    for q in QUERIES:
        print(f"🔹 QUERY: '{q}'")
        try:
            resp = requests.post(URL, json={"message": q}, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                reply = data.get("reply", "NO REPLY")
                movies = data.get("movies", [])
                print(f"🔸 REPLY: {reply}")
                if movies:
                    print(f"🔸 MOVIES Found: {len(movies)}")
                    for m in movies[:2]: # Show first 2
                        print(f"   - {m.get('title')} (ID: {m.get('id')})")
            else:
                print(f"❌ ERROR: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
        print("-" * 40)

if __name__ == "__main__":
    test_chatbot()
