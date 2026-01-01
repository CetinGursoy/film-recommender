import numpy as np
from collections import defaultdict

def recommend_by_collab(user_id, ratings, movies, top_n=20):
    """
    ratings: List[Rating] ORM objeleri
    movies: List[Movie]
    """

    # Kullanıcının oy verdiği filmler
    user_ratings = {r.movie_id: r.rating for r in ratings if r.user_id == user_id}

    if not user_ratings:
        return []   

    # Filmlere göre kullanıcı listesi
    movie_to_users = defaultdict(dict)
    for r in ratings:
        movie_to_users[r.movie_id][r.user_id] = r.rating

    # Kullanıcı benzerlik hesaplama (cosine similarity)
    similarities = defaultdict(float)

    for other_user in set(r.user_id for r in ratings):
        if other_user == user_id:
            continue

        # Ortak filmler
        common_movies = [
            m for m in user_ratings if m in movie_to_users and other_user in movie_to_users[m]
        ]

        if not common_movies:
            continue

        v1 = np.array([user_ratings[m] for m in common_movies])
        v2 = np.array([movie_to_users[m][other_user] for m in common_movies])

        # Cosine
        sim = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        similarities[other_user] = sim

    # En benzer kullanıcıyı bul
    if not similarities:
        return []

    top_user = max(similarities, key=similarities.get)

    # Benzer kullanıcının sevdiği filmleri çıkar
    recs = []
    for movie_id, rating in movie_to_users.items():
        if top_user in rating and movie_id not in user_ratings:
            recs.append(movie_id)

    results = []
    for m in movies:
        if m.id in recs:
            results.append({
                "id": m.id,
                "title": m.title,
                "poster_path": m.poster_path,
                "overview": m.overview,
                "vote_average": m.vote_average,
                "popularity": m.popularity,
            })

    return results[:top_n]
