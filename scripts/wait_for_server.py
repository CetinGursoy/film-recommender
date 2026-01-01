import requests
import time

URL = "http://localhost:8000/movies/popular"

print("Waiting for server to come up...")
start = time.time()
while True:
    try:
        r = requests.get(URL, timeout=2)
        if r.status_code == 200:
            print(f"✅ Server is UP! (Took {time.time() - start:.1f}s)")
            break
    except:
        pass
    print(".", end="", flush=True)
    time.sleep(2)
