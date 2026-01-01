
import sqlite3
import json

def check_db():
    conn = sqlite3.connect("app/movies.db")
    c = conn.cursor()
    
    # Check Kolpaçino (for Şafak Sezer)
    c.execute('SELECT id, title, "cast" FROM movies WHERE title LIKE "%Kolpaçino%" LIMIT 1')
    res = c.fetchone()
    if res:
        print(f"🎬 Title: {res[1]}")
        print(f"👥 Cast (Raw): {res[2][:100]}...") # Print first 100 chars
    else:
        print("❌ Kolpaçino not found")

    # Check Recep İvedik
    c.execute('SELECT id, title, "cast" FROM movies WHERE title LIKE "%Recep İvedik%" LIMIT 1')
    res = c.fetchone()
    if res:
        print(f"🎬 Title: {res[1]}")
    else:
        print("❌ Recep İvedik not found")

    conn.close()

if __name__ == "__main__":
    check_db()
