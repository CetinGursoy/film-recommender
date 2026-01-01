
import requests
import datetime

def verify_upcoming():
    try:
        response = requests.get("http://127.0.0.1:8000/movies/upcoming")
        if response.status_code != 200:
            print(f"❌ Error: Status {response.status_code}")
            return

        movies = response.json()
        print(f"🔍 Found {len(movies)} upcoming movies.")
        
        today = datetime.date.today().isoformat()
        errors = 0
        
        for m in movies:
            title = m.get('title')
            date = m.get('release_date')
            rating = m.get('vote_average')
            
            print(f"- {title} | Date: {date} | Rating: {rating}")
            
            if rating != 0.0:
                print(f"  ❌ FAIL: Rating is not 0.0 (Found: {rating})")
                errors += 1
                
            if date <= today:
                print(f"  ❌ FAIL: Date is not in future (Found: {date}, Today: {today})")
                errors += 1
                
        if errors == 0:
            print("\n✅ All checks passed! Only future movies with 0.0 rating found.")
        else:
            print(f"\n❌ Found {errors} errors.")
            
    except Exception as e:
        print(f"❌ Script Error: {e}")

if __name__ == "__main__":
    verify_upcoming()
