from sqlalchemy import create_engine, text
from app.db import DATABASE_URL

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Check distinct languages found so far
    result = conn.execute(text("SELECT original_language, COUNT(*) FROM movies GROUP BY original_language"))
    rows = result.fetchall()
    print("Language distribution:")
    for row in rows:
        print(row)
        
    # Check specifically for 'tr'
    tr_count = conn.execute(text("SELECT COUNT(*) FROM movies WHERE original_language = 'tr'")).scalar()
    print(f"Movies with original_language='tr': {tr_count}")
