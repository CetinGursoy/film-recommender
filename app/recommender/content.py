import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import json

def recommend_by_content(movies, seed_movie=None, top_n=20):
    """
    movies         : tüm Movie objeleri
    seed_movie     : belirli bir filme göre öneri olsun istiyorsan Movie objesi
    top_n          : kaç öneri istiyorsun
    """

    if not movies:
        return []

   
    # 1)  (title + overview + GENRES + DIRECTORS + CAST)
   
    corpus = []
    
    for m in movies:
        
        genre_str = ""
        try:
            if m.genres:
                g_list = json.loads(m.genres) if isinstance(m.genres, str) else m.genres
                if isinstance(g_list, list):
                    genre_str = " ".join([g.get('name', '') if isinstance(g, dict) else str(g) for g in g_list] * 5)
        except:
            pass

        
        director_str = ""
        try:
            if m.directors:
                d_list = json.loads(m.directors) if isinstance(m.directors, str) else m.directors
                if isinstance(d_list, list):
                    director_str = " ".join([d.get('name', '').replace(" ", "") for d in d_list] * 3)
        except:
            pass

        cast_str = ""
        try:
            if m.cast:
                c_list = json.loads(m.cast) if isinstance(m.cast, str) else m.cast
                if isinstance(c_list, list):
                    
                    cast_str = " ".join([c.get('name', '').replace(" ", "") for c in c_list[:3]] * 2)
        except:
            pass
            
        text = f"{m.title} {m.overview or ''} {genre_str} {director_str} {cast_str}"
        corpus.append(text)

   
    
   
    tfidf = TfidfVectorizer(stop_words="english")
    try:
        matrix = tfidf.fit_transform(corpus)
    except ValueError:
        return []

    
    
    
    if seed_movie:
        try:
            anchor_index = movies.index(seed_movie)
        except ValueError:
            anchor_index = np.argmax([m.popularity for m in movies])
    else:
        anchor_index = np.argmax([m.popularity for m in movies])

    
   
    
    similarities = cosine_similarity(matrix[anchor_index:anchor_index + 1], matrix).flatten()

    # Kendini çıkar
    similarities[anchor_index] = -1  

    # En benzer filmleri bul
    indices = similarities.argsort()[::-1][:top_n]

    
    # 5) JSON formatında döndür
    
    recommended = []
    for idx in indices:
        m = movies[idx]
        recommended.append({
            "id": m.id,
            "title": m.title,
            "poster_path": m.poster_path,
            "overview": m.overview,
            "vote_average": m.vote_average,
            "popularity": m.popularity,
        })

    return recommended
