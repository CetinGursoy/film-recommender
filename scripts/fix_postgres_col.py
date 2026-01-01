import os
from dotenv import load_dotenv

# 1. Load env vars FIRST
load_dotenv()

# Verify we have a DATABASE_URL
print("DATABASE_URL:", os.getenv("DATABASE_URL"))

from sqlalchemy import create_engine, text
from app.db import DATABASE_URL

# Double check
print("Imported DATABASE_URL:", DATABASE_URL)

engine = create_engine(DATABASE_URL)

def fix_column():
    print("Checking 'original_language' column in Postgres...")
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE movies ADD COLUMN original_language VARCHAR"))
            conn.commit()
            print("SUCCESS: Added 'original_language' column.")
    except Exception as e:
        print(f"Info/Error: {e}")
        # Possibly it exists or something else.
        # Let's verify existence.
        try:
             with engine.connect() as conn:
                 conn.execute(text("SELECT original_language FROM movies LIMIT 1"))
                 print("Column definitely exists now.")
        except Exception as e2:
             print(f"STILL FAILING: {e2}")

if __name__ == "__main__":
    fix_column()
