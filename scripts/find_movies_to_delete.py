
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

movies_to_find = [
    "Doğulu",
    "Sevimli Haydut",
    "Yuvasız Kuşlar",
    "Zaferin Rengi"
]

with engine.connect() as connection:
    for title in movies_to_find:
        result = connection.execute(text("SELECT id, title FROM movies WHERE title = :title"), {"title": title}).fetchone()
        if result:
            print(f"Found: {result.title} (ID: {result.id})")
        else:
            print(f"Not Found: {title}")
