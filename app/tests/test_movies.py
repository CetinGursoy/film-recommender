from app.tests.conftest import TestingSessionLocal
from app import models_backup

def seed_movies():
    db = TestingSessionLocal()

    db.query(models_backup.Movie).delete()

    movie1 = models_backup.Movie(
        title="Inception",
        genre="Sci-Fi",
        description="A mind-bending movie about dreams within dreams.",
    )
    movie2 = models_backup.Movie(
        title="The Matrix",
        genre="Sci-Fi",
        description="A hacker discovers the nature of his reality.",
    )

    db.add_all([movie1, movie2])
    db.commit()
    db.refresh(movie1)
    db.refresh(movie2)
    db.close()

    return movie1, movie2
