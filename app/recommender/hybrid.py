from .content import recommend_by_content
from .collab import recommend_by_collab

def hybrid_recommend(user_id, movies, ratings, top_n=20):
    
    content_list = recommend_by_content(movies, top_n=50)

    
    collab_list = recommend_by_collab(user_id, ratings, movies, top_n=50)

    
    scores = {}

   
    for i, m in enumerate(content_list):
        scores[m["id"]] = scores.get(m["id"], 0) + (60 - i)

    
    for i, m in enumerate(collab_list):
        scores[m["id"]] = scores.get(m["id"], 0) + (40 - i)

    
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    
    final = []
    for movie_id, score in ranked[:top_n]:
        for m in movies:
            if m.id == movie_id:
                final.append({
                    "id": m.id,
                    "title": m.title,
                    "poster_path": m.poster_path,
                    "overview": m.overview,
                    "vote_average": m.vote_average,
                    "popularity": m.popularity,
                    "score": score,
                })
                break

    return final
