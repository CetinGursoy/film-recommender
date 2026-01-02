import sys
import os
sys.path.append(os.getcwd())

from app.models.collection import Collection
from app.models.watched import Watched
from app.models.watchlist import Watchlist
from app.models.users import User
from app.models.like import Like
from app.models.rating import Rating
from app.models.review import Review
from app.models.lists import ListItem
from app.models.movie import Movie
from app.db import SessionLocal
from sqlalchemy import or_

db = SessionLocal()

print("\n--- CHECK POPULAR MOVIES (FALLBACK) ---")
popular = db.query(Movie).order_by(Movie.popularity.desc()).limit(5).all()
for m in popular:
    print(f" - {m.title} (Pop: {m.popularity})")

print("\n--- TEST RECOMMENDATION ROTATION ---")
from app.services.recommendation import recommend_by_genre, recommend_by_actor

# Find a user with likes
first_like = db.query(Like).order_by(Like.id.desc()).first() # Most active user?
if not first_like:
    print("❌ No likes found. Cannot test recommendation.")
else:
    user_id = first_like.user_id
    print(f"Testing for User ID: {user_id}")
    
    # Call 1
    print("\n[Call 1] recommend_by_genre(exclude=[])")
    recs1, genres1 = recommend_by_genre(db, user_id, exclude_ids=[], limit=3)
    ids1 = []
    if not recs1:
         print("⚠️ Call 1 returned EMPTY! (Maybe falling back to popular?)")
    else:
         for m in recs1: print(f" - {m.title}")
         ids1 = [m.id for m in recs1]
    
    # Call 2 (Exclude previous)
    print(f"\n[Call 2] recommend_by_genre(exclude={ids1})")
    recs2, genres2 = recommend_by_genre(db, user_id, exclude_ids=ids1, limit=3)
    if not recs2:
         print("⚠️ Call 2 returned EMPTY! (This would cause fallback to popular)")
    else:
         for m in recs2: print(f" - {m.title}")
         
    # Call 3 (Actor based)
    print(f"\n[Call 3] recommend_by_actor(exclude={ids1})")
    recs3, actors = recommend_by_actor(db, user_id, exclude_ids=ids1, limit=3)
    if not recs3:
         print("⚠️ Call 3 (Actor) returned EMPTY!")
    else:
         for m in recs3: print(f" - {m.title}")

db.close()
