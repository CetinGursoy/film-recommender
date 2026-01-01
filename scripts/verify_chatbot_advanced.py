
import requests

BASE_URL = "http://127.0.0.1:8000/chatbot/ask"

def test_query(message):
    print(f"\n❓ Soru: '{message}'")
    try:
        response = requests.post(BASE_URL, json={"message": message})
        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply", "")
            print(f"🤖 Cevap: {reply}")
            movies = data.get("movies", [])
            for m in movies:
                print(f"  - {m['title']}")
        else:
            print(f"❌ Hata: {response.status_code}")
    except Exception as e:
        print(f"💥 İstek hatası: {e}")

if __name__ == "__main__":
    # Test 1: Yönetmen + Filler words
    test_query("David Leitch yönettiği film")
    
    # Test 2: Benzer
    test_query("Cem Yılmaz ile benzer filmler")
    
    # Test 3: Standart
    test_query("Al Pacino")
