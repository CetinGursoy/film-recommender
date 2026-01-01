
from app.db import SessionLocal
from app.models.users import User
from app.models.review import Review
from app.models.collection import Collection
from app.models.watched import Watched # Fix for mapping error # Fix for mapping error

def check_ceg_reviews():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "ceg").first()
        if not user:
            print("User 'ceg' not found!")
            return

        print(f"User 'ceg' found. ID: {user.id}")
        
        reviews = db.query(Review).filter(Review.user_id == user.id).all()
        print(f"Found {len(reviews)} reviews for 'ceg'.")
        for r in reviews:
            print(f"- Review ID: {r.id}, Movie ID: {r.movie_id}, Text: {r.text}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_ceg_reviews()
