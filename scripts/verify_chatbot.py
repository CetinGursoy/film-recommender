
import requests
import json

BASE_URL = "http://127.0.0.1:8000/chatbot/ask"

def test_query(message):
    print(f"\n❓ Soru: '{message}'")
    try:
        response = requests.post(BASE_URL, json={"message": message})
        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply", "")
            movies = data.get("movies", [])
            print(f"🤖 Cevap: {reply}")
            if movies:
                print(f"🎬 Önerilenler ({len(movies)}):")
                for m in movies:
                    print(f"  - {m['title']}")
            else:
                print("⚠️ Film önerisi yok.")
        else:
            print(f"❌ Hata: {response.status_code}")
    except Exception as e:
        print(f"💥 İstek hatası: {e}")

if __name__ == "__main__":
    # Test 1: Türk Filmleri
    test_query("bana türk filmi öner")
    
    # Test 2: Suffix handling (Cem Yılmaz'ın -> Cem Yılmaz)
    test_query("Cem Yılmaz'ın filmleri neler?")
    
    # Test 3: Normal search
    test_query("Matrix izle")
