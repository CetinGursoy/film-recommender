
import os
import pickle
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Singleton Logic
_model = None
_movie_embeddings = {}  # {movie_id: vector}
_movie_metadata = {}    # {movie_id: {title, poster}}

# 🔥 MULTILINGUAL MODEL (Türkçe için çok daha iyi)
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_FILE = "movie_embeddings.pkl" # Triggers reload

def load_model():
    global _model
    if _model is None:
        print("🧠 NLP Model Yükleniyor (Bu işlem ilk seferde biraz sürebilir)...")
        _model = SentenceTransformer(MODEL_NAME)
        print("✅ NLP Model Yüklendi!")
    return _model

def generate_embeddings_for_db(movies):
    """
    Veritabanındaki filmlerin özetlerini (overview_tr veya overview) vektöre çevirir.
    Cache mekanizması eklendi: Pickle dosyasından okur, yoksa oluşturup kaydeder.
    """
    global _movie_embeddings, _movie_metadata, _model
    
    # 1. Try Loading from Cache
    if os.path.exists(EMBEDDING_FILE):
        print(f"📂 Embedding önbelleği bulundu: {EMBEDDING_FILE}")
        try:
            with open(EMBEDDING_FILE, "rb") as f:
                data = pickle.load(f)
                _movie_embeddings = data.get("embeddings", {})
                _movie_metadata = data.get("metadata", {})
                print(f"✅ {_len(_movie_embeddings)} film önbellekten yüklendi!")
                
                # Check if we need to update (simple check: count)
                if len(_movie_embeddings) >= len(movies):
                    return
                print("⚠ Yeni filmler var, tekrar hazırlanıyor...")
        except Exception as e:
            print(f"❌ Önbellek okuma hatası: {e}")

    # 2. If no cache or update needed, generate fresh
    model = load_model()
    
    print(f"🔄 {len(movies)} film için embedding hazırlanıyor...")
    
    texts = []
    ids = []
    
    _movie_embeddings = {}
    _movie_metadata = {}

    for m in movies:
        # Öncelik Türkçe özet, yoksa İngilizce, o da yoksa başlık
        summary = m.overview_tr if m.overview_tr else (m.overview if m.overview else "")
        
        # Clean Cast/Director (Json to String)
        import json
        
        cast_str = ""
        try:
            if m.cast:
                # Handle simplified list of dicts or just string
                # If it's already a string, check if it's json
                cast_data = json.loads(m.cast) if isinstance(m.cast, str) else m.cast
                if isinstance(cast_data, list):
                    names = [p.get("name", "") for p in cast_data if p.get("name")]
                    cast_str = ", ".join(names[:5]) # Top 5 actors
        except:
            cast_str = str(m.cast)

        director_str = ""
        try:
            if m.directors:
                dir_data = json.loads(m.directors) if isinstance(m.directors, str) else m.directors
                if isinstance(dir_data, list):
                    names = [d.get("name", "") for d in dir_data if d.get("name")]
                    director_str = ", ".join(names)
        except:
             director_str = str(m.directors)

        # Zenginleştirilmiş Metin (Metadata + Özet) with HEAVY WEIGHTING
        # Repeat title, genres AND OVERVIEW to give them more importance in the embedding
        rich_text = f"Film: {m.title}. {m.title}. " # Title repeated for weighting
        if m.genres: rich_text += f"Tür: {m.genres}. {m.genres}. " # Genres repeated
        if director_str: rich_text += f"Yönetmen: {director_str}. "
        if cast_str: rich_text += f"Oyuncular: {cast_str}. "
        # OVERVIEW 2x WEIGHTING - Critical for theme-based search
        rich_text += f"Özet: {summary}. {summary}" # Overview repeated for weighting
        
        texts.append(rich_text)
        ids.append(m.id)
        
        _movie_metadata[m.id] = {
            "title": m.title,
            "poster": m.poster_url or m.poster_path
        }

    if texts:
        embeddings = model.encode(texts, convert_to_numpy=True)
        
        for i, movie_id in enumerate(ids):
            _movie_embeddings[movie_id] = embeddings[i]
            
        # 3. Save to Cache
        try:
            with open(EMBEDDING_FILE, "wb") as f:
                pickle.dump({
                    "embeddings": _movie_embeddings,
                    "metadata": _movie_metadata
                }, f)
            print("💾 Embeddingler diske kaydedildi.")
        except Exception as e:
            print(f"❌ Kaydetme hatası: {e}")
            
    print("✅ Embedding işlemi tamamlandı!")

def _len(d):
    return len(d) if d else 0

def semantic_search(query, top_k=3, score_threshold=0.5):
    """
    Kullanıcının sorgusunu (örn: 'beni ağlatan film') vektöre çevirip
    en yakın filmleri bulur.
    
    Args:
        query: Search query text
        top_k: Maximum number of results
        score_threshold: Minimum cosine similarity score (0-1). Default 0.5
    """
    global _movie_embeddings, _movie_metadata
    
    model = load_model()
    
    if not _movie_embeddings:
        return []

    # Sorgu vektörü
    query_vec = model.encode([query], convert_to_numpy=True)
    
    # Tüm film vektörleri
    movie_ids = list(_movie_embeddings.keys())
    movie_vecs = np.array(list(_movie_embeddings.values()))
    
    if len(movie_vecs) == 0:
        return []

    # Benzerlik hesabı (Cosine Similarity)
    scores = cosine_similarity(query_vec, movie_vecs)[0]
    
    # En yüksek skorlu indexler
    top_indices = np.argsort(scores)[::-1][:top_k]
    
    results = []
    for idx in top_indices:
        score = scores[idx]
        if score < score_threshold: 
            continue # Eşik altındakileri atla
        
        m_id = movie_ids[idx]
        meta = _movie_metadata.get(m_id)
        if meta:
            results.append({
                "id": m_id,
                "title": meta["title"],
                "poster": meta["poster"],
                "score": float(score)
            })
            
    return results
