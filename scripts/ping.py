import requests
try:
    r = requests.get("http://localhost:8000/movies/popular", timeout=5)
    print(r.status_code)
except Exception as e:
    print(e)
