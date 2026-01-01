
import requests
import json
import urllib.parse

def check_search(query):
    encoded_query = urllib.parse.quote(query)
    url = f"http://localhost:8000/chatbot/debug-search?query={encoded_query}"
    print(f"Requesting: {url}")
    try:
        res = requests.get(url, timeout=10)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            print(json.dumps(res.json(), indent=2, ensure_ascii=False))
        else:
            print(res.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_search("cem yılmaz filmi öner")
