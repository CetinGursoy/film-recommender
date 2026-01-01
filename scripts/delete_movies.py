
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

ids_to_delete = [1548, 1301, 1259, 1282] 

with engine.connect() as connection:
    print(f"Deleting movies with IDs: {ids_to_delete}")
    
    # Check if they exist before deleting
    for movie_id in ids_to_delete:
        result = connection.execute(text("SELECT title FROM movies WHERE id = :id"), {"id": movie_id}).fetchone()
        if result:
            connection.execute(text("DELETE FROM movies WHERE id = :id"), {"id": movie_id})
            connection.commit()
            print(f"Deleted: {result.title} (ID: {movie_id})")
        else:
            print(f"Movie ID {movie_id} not found (already deleted?)")

print("Deletion complete.")
