# app/main.py

from dotenv import load_dotenv
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, "..", ".env")

print("ENV DOSYASI:", ENV_PATH)
load_dotenv(dotenv_path=ENV_PATH)

from app.db import Base, engine, SessionLocal
from app.utils.init_data import import_local_movies, update_movie_posters
from app.services.tmdb_import import add_movies_to_db
from app.routers import (
    auth, users, movies, ratings, reviews, lists, admin, recommend, likes, collections, chatbot, contact, watched, user_actions, dashboard, trivia
)





app = FastAPI(title="Film Recommender API", version="1.0.0")

@app.get("/debug-env")
def debug_env():
    return {
        "TMDB_API_KEY": os.getenv("TMDB_API_KEY"),
        "TMDB_V4_TOKEN": os.getenv("TMDB_V4_TOKEN")
    }

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB tabloları
Base.metadata.create_all(bind=engine)

# OPENAPI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title="Film Recommender API",
        version="1.0.0",
        routes=app.routes,
    )
    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi


@app.on_event("startup")
def startup_event():
    print("🔥 STARTUP BAŞLADI...")

    # 1) 1500 yerel film
    import_local_movies()

    # 2) TMDB popüler + upcoming
    db = SessionLocal()
    from app.models.movie import Movie
    add_movies_to_db(db, Movie)
    db.close()

    # 3) Poster update
    update_movie_posters()

    print("🔥 STARTUP TAMAMLANDI (1500 + TMDB)")

# ROUTERS
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(movies.router)
app.include_router(ratings.router)
app.include_router(reviews.router)
app.include_router(lists.router)
app.include_router(likes.router)
app.include_router(admin.router)
app.include_router(recommend.router)
app.include_router(collections.router)
app.include_router(chatbot.router)
app.include_router(contact.router)
app.include_router(watched.router)
app.include_router(user_actions.router)
app.include_router(dashboard.router)
app.include_router(trivia.router)

@app.get("/")
def home():
    return {"message": "Film Recommender Backend Running!"}
