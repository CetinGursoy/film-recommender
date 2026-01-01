
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.security import get_current_user_optional
from app.services.nlp_filter import is_clean
from app.services.recommendation import recommend_personal
from app.models.movie import Movie
from sqlalchemy import or_
from app.services.nlp_service import generate_embeddings_for_db, semantic_search
from app.db import SessionLocal
from thefuzz import process

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

# Force Reload Timestamp
# Added personalized recommendations from liked movies.

# 🔥 STARTUP: Embeddings Yükle
@router.on_event("startup")
def load_embeddings():
    db = SessionLocal()
    movies = db.query(Movie).all()
    generate_embeddings_for_db(movies)
    
    # Cache Popular People for Fuzzy Search
    global POPULAR_PEOPLE
    POPULAR_PEOPLE = set()
    # Simplified: Get all actors from top 500 movies?
    # Or just iterate all and collect unique names (might be heavy?)
    # Let's verify execution time. 1600 movies is fine.
    import json
    for m in movies:
        try:
             cast = json.loads(m.cast) if isinstance(m.cast, str) else m.cast
             if cast:
                 for p in cast[:3]: # Top 3 actors per movie
                     if p.get("name"): POPULAR_PEOPLE.add(p["name"])
             
             dirs = json.loads(m.directors) if isinstance(m.directors, str) else m.directors
             if dirs:
                 for d in dirs:
                     if d.get("name"): POPULAR_PEOPLE.add(d["name"])
        except:
             pass
    print(f"🧶 Fuzzy Search için {len(POPULAR_PEOPLE)} kişi hafızaya alındı.")
    
    db.close()

@router.post("/ask")
async def ask_chatbot(
    msg: dict = Body(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional)
):
    text = msg.get("message", "").strip()
    if not text:
        return {"reply": "...", "action": "none"}
    
    text_lower = text.lower()

    if not is_clean(text_lower):
        return {
            "reply": "Lütfen saygılı bir dil kullanalım. Size nasıl yardımcı olabilirim?",
            "action": "none"
        }

    # 1. SOHBET / CHITTER CHATTER
    greetings = ["merhaba", "selam", "hi", "hello", "naber", "günaydın", "iyi akşamlar", "selamlar"]
    if any(x in text_lower for x in greetings):
        return {
            "reply": "Merhaba! Ben FilmRec asistanıyım. Sana film önerebilir, teknik destek verebilir veya hesabınla ilgili yardımcı olabilirim. Ne istersin?",
            "action": "none"
        }

    if any(x in text_lower for x in ["nasılsın", "nasıl gidiyor", "ne haber"]):
        return {"reply": "Harikayım! Film izlemek (daha doğrusu önermek) beni mutlu ediyor. Sen nasılsın?"}
    
    if any(x in text_lower for x in ["ben de iyiyim", "ben iyiyim", "bende iyiyim"]):
        return {"reply": "Sana ne önermemi istersin? 🤖"}

    if any(x in text_lower for x in ["teşekkür", "tesekkür", "sağol", "eyvallah"]):
        return {"reply": "Rica ederim! İyi seyirler 🍿"}

    if any(x in text_lower for x in ["kimsin", "adın ne", "sen kimsin"]):
        return {"reply": "Ben FilmRec Asistanı. Senin film zevkini çözüp nokta atışı öneriler yapmak için buradayım."}

    # 1.5 UPCOMING / YAKINDA OLANLAR
    # "Yakındaki filmler" butonu veya benzer sorgular için
    upcoming_keywords = ["yakında", "gelecek", "vizyon", "ne zaman", "geliyor"]
    # Check if query contains any upcoming keyword - but careful not to overlap generic questions
    # "Yakındaki filmler" is specific.
    if any(k in text_lower for k in upcoming_keywords):
        from datetime import date
        today = date.today().isoformat()
        
        # Gelecek filmleri bul (Release date > today)
        # release_date string format YYYY-MM-DD usually.
        upcoming_movies = (db.query(Movie)
                           .filter(Movie.release_date > today)
                           .order_by(Movie.release_date.asc())
                           .limit(5).all())
        
        if upcoming_movies:
             return {
                "reply": "Yakında vizyona girecek şu filmleri buldum:",
                "movies": [{"id": m.id, "title": m.title, "poster": m.poster_url or m.poster_path} for m in upcoming_movies]
            }
        else:
            return {
                "reply": "Şu an için veritabanımda yakın tarihli bir film görünmüyor."
            }

    # 2. GENRE DETECTION (En yüksek öncelik - "Komedi filmi aç" deyince komedi gelmeli)
    genres_map = {
        "aksiyon": "Action", "komedi": "Comedy", "dram": "Drama",
        "bilim": "Science Fiction", "kurgu": "Science Fiction", "teknoloji": "Science Fiction",
        "korku": "Horror", "gerilim": "Thriller", "suç": "Crime",
        "macera": "Adventure", "romantik": "Romance", 
        "animasyon": "Animation", "aile": "Family", "savaş": "War",
        "tarih": "History", "gizem": "Mystery", "western": "Western"
    }

    # Keywords for "New / Latest"
    new_intent_keywords = ["yeni", "son", "2024", "2025", "güncel", "en yeni", "yakın"]
    is_new_intent = any(k in text_lower for k in new_intent_keywords)

    # SESSION MEMORY STORAGE
    # Global dict to store context. In a real app, use Redis.
    # Structure: { session_id: { "last_genre": ("komedi", "Comedy"), "last_actor": "Cem Yılmaz", "last_intent": "genre_search" } }
    global SESSION_MEMORY
    try:
        SESSION_MEMORY
    except NameError:
        SESSION_MEMORY = {}

    session_id = msg.get("session_id")
    context = SESSION_MEMORY.get(session_id, {}) if session_id else {}

    # Keywords for "Refinement / Continuation"
    refinement_keywords = ["daha", "başka", "yenileri", "eskileri", "peki", "ya", "değil"]
    is_refinement = any(k in text_lower for k in refinement_keywords) and len(text.split()) < 5
    
    # Merge Context if Refinement
    if is_refinement and context:
        print(f"🧠 Context Merging Triggered for {session_id}: {context}")
        
        # If user says "Daha yenileri", keep genre but change sort intent
        if "yenileri" in text_lower or "yeni" in text_lower:
            is_new_intent = True
            
        # If user says "Peki aksiyon?", override genre
        # We let standard detection run first, if it finds a new genre, it overrides.
        
    # 2. GENRE DETECTION (Multi-Genre Support with Fuzzy)
    found_genres = set()
    
    # 2.1 Exact Match First
    for k, v in genres_map.items():
        if k in text_lower:
            found_genres.add((k, v))
            
    # 2.2 Fuzzy Match (if no exact found)
    # Tokenize input and check against genre keys
    # Only if exact detection failed or just to augment? 
    # Let's augment but be strict (80%)
    
    tokens = text_lower.split()
    genre_keys = list(genres_map.keys())
    
    for t in tokens:
        # Skip very short words to avoid false positives
        if len(t) < 4: continue
        
        # Don't fuzzy match if it's already an exact match in the text
        if any(k in t for k in genre_keys): continue

        match = process.extractOne(t, genre_keys)
        if match:
            best_match, score = match
            if score >= 80:
                print(f"🧶 Fuzzy Genre Match: '{t}' -> '{best_match}' ({score}%)")
                found_genres.add((best_match, genres_map[best_match]))

    # If no genres found BUT we have context and it's a refinement/short query
    if not found_genres and context.get("last_genres") and (is_refinement or len(text.split()) < 4):
         # Restore last genres
         print(f"🔄 Restoring context genres: {context['last_genres']}")
         found_genres = set(tuple(x) for x in context['last_genres']) # Ensure tuples


    # ... Deduplication logic ...
    
    unique_genre_values = set()
    display_genre_names = []
    
    for k, v in found_genres:
        if v not in unique_genre_values:
            unique_genre_values.add(v)
            display_genre_names.append(k.capitalize())
            
    is_pure_genre_query = False
    
    if unique_genre_values:
        # Check if query is "pure" (mostly just genre words + noise)
        noise = ["filmleri", "filmi", "film", "öner", "listele", "aç", "getir", "var", "mı", "boşluk", "bana", "ve", "ile", "daha", "yenileri", "olan"] 
        all_noise = noise + new_intent_keywords
        
        clean_t = text_lower
        for k, v in found_genres:
            clean_t = clean_t.replace(k, "") # Remove genre words
            
        for n in all_noise:
            clean_t = clean_t.replace(n, "").strip() # Remove noise
            
        # If nearly empty OR it was explicitly a context restoration
        if len(clean_t) < 3 or (context.get("last_genres") and not is_refinement == False):
            is_pure_genre_query = True

    if is_pure_genre_query and unique_genre_values:
        # SAVE CONTEXT
        if session_id:
            SESSION_MEMORY[session_id] = {
                "last_genres": list(found_genres), # Save as list of tuples
                "last_intent": "genre"
            }
            
        query_base = db.query(Movie)
        
        # Apply AND logic for all found genres
        for g_val in unique_genre_values:
            query_base = query_base.filter(Movie.genres.like(f"%{g_val}%"))
        
        if is_new_intent:
             movies = query_base.order_by(Movie.release_date.desc()).limit(5).all()
             joined_names = " - ".join(display_genre_names)
             reply_msg = f"İşte senin için en yeni {joined_names} filmleri:"
        else:
             movies = query_base.order_by(Movie.vote_average.desc()).limit(5).all()
             joined_names = " - ".join(display_genre_names)
             reply_msg = f"İşte senin için en iyi {joined_names} filmleri (Bağlam: {joined_names}):"

        return {
            "reply": reply_msg,
            "movies": [{"id": m.id, "title": m.title, "poster": m.poster_url or m.poster_path} for m in movies]
        }

    # 3. YARDIMCI FONKSİYONLAR VE ARAMA HAZIRLIĞI
    stopwords = {
        "filmleri", "filmi", "oynadığı", "yönettiği", "yönetmen", "kimdir", "öner", "bana", "hakkında", "izle", 
        "var", "mi", "mı", "mu", "mü", "film", "benzer", "tarzı", "gibi", "ile", "ve", "veya", "olan", "yapan", "listele", "göster", "getir", "bul",
        "filmii", "flimi", "fılm", "fılmı", "oner", "hngi", "yapım" # Common typos
    }
    
    suffixes = [
        "'tan", "'ten", "'dan", "'den", "'nın", "'nin", "'nun", "'nün",
        "'lar", "'ler", "'ta", "'te", "'da", "'de", "'ın", "'in", "'un", "'ün", "'a", "'e", "'",
        "tan", "ten", "dan", "den", "nın", "nin", "nun", "nün",
        "lar", "ler", "ta", "te", "da", "de", "ın", "in", "un", "ün", "a", "e"
    ]

    def clean_tokens(query):
        # 1. Tokenize
        tokens = query.split()
        cleaned_tokens = []
        
        for t in tokens:
            # 2. Strict Stopword Check
            if t in stopwords: continue
            
            # 3. Fuzzy Stopword Check (Basic - if it looks like 'filmi' etc)
            # Simple length check to avoid destroying short words
            if len(t) > 3:
                is_stop = False
                for sw in stopwords:
                    if len(sw) > 3 and sw in t: # Substring check (lazy fuzzy)
                        # "filmii" contains "film"
                         pass 
                
            # 4. Suffix Stripping (Per Token)
            # Try to strip suffix if it makes the word a valid name part?
            # Or just strip generally.
            candidate = t
            for s in suffixes:
                if candidate.endswith(s):
                    # Check if stripping leaves enough chars
                    stripped = candidate[:-len(s)]
                    if len(stripped) >= 3: # "Cem" is 3 chars. "Ali" is 3. 
                        candidate = stripped
                        break # Strip only longest match
            
            cleaned_tokens.append(candidate)
            
        return " ".join(cleaned_tokens).strip()

    search_query = clean_tokens(text_lower)
    
    import json
    from sqlalchemy import or_

    def generate_search_variants(q):
        variants = {q}
        
        # 1. Turkish Character Map (For Anglicization)
        # i -> i works for anglicization
        tr_map = {"ı": "i", "ğ": "g", "ü": "u", "ş": "s", "ö": "o", "ç": "c", "İ": "I", "I": "i"}
        anglicized = "".join(tr_map.get(c, c) for c in q)
        variants.add(anglicized)

        # 2. proper Capitalization
        def tr_capitalize(text):
            words = text.split()
            cap_words = []
            for w in words:
                if not w: continue
                first = w[0]
                rest = w[1:]
                if first == "i": first = "İ"
                elif first == "ı": first = "I"
                else: first = first.upper()
                cap_words.append(first + rest)
            return " ".join(cap_words)

        titled = tr_capitalize(q) 
        variants.add(titled)
        variants.add(titled.upper())

        # 3. JSON Escape MANUAL (Robust)
        # Manually verify encoding for troublesome Turkish chars
        escape_map = {
            "ş": "\\u015f", "Ş": "\\u015e",
            "ı": "\\u0131", "İ": "\\u0130", 
            "ğ": "\\u011f", "Ğ": "\\u011e",
            "ü": "\\u00fc", "Ü": "\\u00dc",
            "ö": "\\u00f6", "Ö": "\\u00d6",
            "ç": "\\u00e7", "Ç": "\\u00c7"
        }
        
        def escape_str(s):
            res = ""
            for char in s:
                res += escape_map.get(char, char)
            return res

        variants.add(escape_str(titled))
        variants.add(escape_str(q))
        
        try:
             import json
             dumped_ascii = json.dumps(titled, ensure_ascii=True)
             variants.add(dumped_ascii.strip('"'))
        except:
             pass
                 
        return list(variants)

    def search_people(query):
        if len(query) < 3: return None # Increased min length slightly
        variants = generate_search_variants(query)
        filters = []
        for v in variants:
            # Hem normal hem escaped versiyonu ara
            filters.append(Movie.cast.ilike(f"%{v}%"))
            filters.append(Movie.directors.ilike(f"%{v}%"))
            
        # Sadece cast/director eşleşmesi
        res = db.query(Movie).filter(or_(*filters)).order_by(Movie.popularity.desc()).limit(10).all()
        return res

    def search_title(query):
        if len(query) < 2: return None
        variants = generate_search_variants(query)
        filters = []
        for v in variants:
            filters.append(Movie.title.ilike(f"%{v}%"))
        # Title öncelikli ama popülerlik ile sırala
        res = db.query(Movie).filter(or_(*filters)).order_by(Movie.popularity.desc()).limit(5).all()
        return res

    # 4. SEARCH EXECUTION
    
    # 4.0 THEME KEYWORD EARLY CHECK
    # If query contains a theme keyword, skip people search and go directly to semantic
    theme_keywords = [
        "mafya", "gangster", "çete", "suç örgütü", "yeraltı",
        "savaş", "asker", "ordu", "cephe",
        "uzay", "galaksi", "gezegen", "astronot",
        "zombi", "vampir", "hayalet", "cin", "doğaüstü",
        "intikam", "öç", "felaket", "kıyamet",
        "dedektif", "cinayet", "soruşturma",
        "hapishane", "mahkum", "kaçış",
        "ağlatan", "hüzünlü", "duygusal", "romantik", "aşk",
        "komik", "güldüren", "eğlenceli",
        "korkunç", "ürkütücü", "gerilimli"
    ]
    
    has_theme_keyword = any(kw in text_lower for kw in theme_keywords)
    
    if has_theme_keyword:
        print(f"🎬 Theme keyword detected, triggering semantic search: {text}")
        semantic_results = semantic_search(text, top_k=5, score_threshold=0.35)
        if semantic_results:
            return {
                "reply": "Aradığın konuya uygun şunları buldum:",
                "movies": semantic_results
            }
        
        # FALLBACK: If semantic search failed, try direct keyword search in overview
        print(f"🔍 Semantic failed, trying overview keyword search for: {text}")
        theme_keyword_found = None
        for kw in theme_keywords:
            if kw in text_lower:
                theme_keyword_found = kw
                break
        
        if theme_keyword_found:
            # Direct LIKE query on overview fields
            overview_results = (db.query(Movie)
                .filter(or_(
                    Movie.overview_tr.ilike(f"%{theme_keyword_found}%"),
                    Movie.overview.ilike(f"%{theme_keyword_found}%")
                ))
                .order_by(Movie.popularity.desc())
                .limit(5).all())
            
            if overview_results:
                return {
                    "reply": f"'{theme_keyword_found}' konulu filmler:",
                    "movies": [{"id": m.id, "title": m.title, "poster": m.poster_url or m.poster_path} for m in overview_results]
                }
    
    # 4.1 People Search (Cem Yılmaz vb.) -> High Priority (only if no theme keyword)
    if len(search_query) > 2 and not has_theme_keyword:
        # ATTEMPT 1: Raw Search
        people_res = search_people(search_query)
        
        # ATTEMPT 2: Split by Apostrophe
        if not people_res and "'" in search_query:
            cleaned = search_query.split("'")[0].strip()
            people_res = search_people(cleaned)

        # ATTEMPT 3: Iterative Suffix Stripping
        if not people_res:
            cleaned = search_query
            found_suffix = False
            for s in suffixes:
                if cleaned.endswith(s):
                    # Remove suffix
                    cleaned = cleaned[:-len(s)].strip()
                    found_suffix = True
                    # If we stripped something significant, try search again
                    if len(cleaned) > 2:
                         people_res = search_people(cleaned)
                         if people_res: 
                             search_query = cleaned # Update query for display
                             break 
                    break 

        # ATTEMPT 4: Fuzzy Search (TheFuzz)
        if not people_res:
             # Check if we have a close match in POPULAR_PEOPLE
             # This is expensive if list is huge, but with 1600 movies * 3 actors ~ 4000 names it is OK.
             global POPULAR_PEOPLE
             try:
                 POPULAR_PEOPLE
             except NameError:
                 POPULAR_PEOPLE = [] # Should be loaded on startup
             
             if POPULAR_PEOPLE:
                 match = process.extractOne(search_query, POPULAR_PEOPLE)
                 if match:
                     best_name, score = match
                     if score >= 85: # High confidence for names
                         print(f"🧶 Fuzzy Person Match: '{search_query}' -> '{best_name}' ({score}%)")
                         people_res = search_people(best_name)
                         search_query = best_name # Update for display 

        if people_res:
             # Use the name that found the result for display if possible, or original query
             name_display = search_query.title()
             if "'" in name_display: name_display = name_display.split("'")[0]
             
             return {
                "reply": f"'{name_display}' (oyuncu/yönetmen) ile ilgili şunları buldum:",
                "movies": [{"id": m.id, "title": m.title, "poster": m.poster_url or m.poster_path} for m in people_res]
            }

    # 4.2 Semantic / Complex Query (Mood based)
    # Eğer cümle uzunsa ve içinde duygu/durum belirten kelimeler varsa, Title aramadan önce Semantic dene.
    # Örn: "Beni ağlatan filmler" -> Title içinde "Ağlatan" aramamalı hemen.
    
    # 4.2.1 SPECIAL CASE: "Gibi / Benzer" Pattern (Intent Conflict Resolution)
    # E.g., "Gora gibi komedi filmi öner"
    # Priority: Find "Gora" first, then add semantic results.
    similarity_keywords = ["gibi", "benzer", "tarzı", "tarzında", "benzeri"]
    has_similarity_intent = any(k in text_lower for k in similarity_keywords)
    
    if has_similarity_intent:
        print(f"🎯 Similarity Intent Detected for: {text}")
        
        # Try to extract the movie title (word(s) BEFORE "gibi" etc.)
        # Simple heuristic: Split by keyword, take the first part.
        title_candidate = text_lower
        for kw in similarity_keywords:
            if kw in title_candidate:
                title_candidate = title_candidate.split(kw)[0].strip()
                break
        
        # Clean title candidate from noise
        noise_words = ["film", "filmi", "bir", "bana", "öner"]
        for nw in noise_words:
            title_candidate = title_candidate.replace(nw, "").strip()
        
        # Search for title
        primary_movie = None
        if len(title_candidate) > 2:
            title_match = db.query(Movie).filter(Movie.title.ilike(f"%{title_candidate}%")).first()
            if title_match:
                primary_movie = title_match
                print(f"🎬 Primary Title Found: {primary_movie.title}")
        
        # Get semantic results based on the FULL query (or title)
        semantic_basis = primary_movie.title if primary_movie else text
        semantic_results = semantic_search(semantic_basis, top_k=4)
        
        # Filter out the primary movie from semantic results to avoid duplication
        if primary_movie and semantic_results:
            semantic_results = [m for m in semantic_results if m.get("id") != primary_movie.id]
        
        if primary_movie:
            # Build combined response
            movies_list = [{"id": primary_movie.id, "title": primary_movie.title, "poster": primary_movie.poster_url or primary_movie.poster_path}]
            
            reply_text = f"'{primary_movie.title}' filmini bulduk!"
            if semantic_results:
                reply_text += " Bu filme benzer diğer önerilerim:"
                movies_list.extend(semantic_results)
            
            return {
                "reply": reply_text,
                "movies": movies_list
            }
        elif semantic_results:
            # No exact title, but semantic found
            return {
                "reply": "Aradığın türde şunları buldum:",
                "movies": semantic_results
            }
    # 4.2.2 THEME/TOPIC-BASED SEMANTIC SEARCH
    # Keywords that indicate user wants a thematic search (not just genre or actor)
    theme_keywords = [
        # Emotions
        "ağlatan", "hüzünlü", "komik", "korkunç", "sürükleyici", "duygusal", "romantik",
        "güldüren", "düşündüren", "heyecanlı", "gerilimli", "ürkütücü",
        # Topics/Themes
        "mafya", "gangster", "çete", "suç örgütü", "yeraltı",
        "savaş", "asker", "ordu", "cephe",
        "uzay", "galaksi", "gezegen", "astronot", "bilim kurgu",
        "zombi", "vampir", "hayalet", "cin", "doğaüstü",
        "aşk", "evlilik", "ilişki", "romantizm",
        "intikam", "öç", "adaletsizlik",
        "hayatta kalma", "survival", "felaket", "kıyamet",
        "dedektif", "cinayet", "gizem", "soruşturma",
        "spor", "futbol", "boks", "basketbol",
        "müzik", "şarkıcı", "konser", "rock", "dans",
        "tarih", "osmanlı", "antik", "ortaçağ", "dünya savaşı",
        "hayal", "rüya", "fantezi", "büyü", "sihir",
        "yapay zeka", "robot", "teknoloji", "hacker",
        "kaçış", "hapishane", "mahkum",
        "aile", "çocuk", "ebeveyn", "çocukluk"
    ]
    
    is_semantic_likely = len(text.split()) > 2 or any(x in text_lower for x in theme_keywords)
    
    if is_semantic_likely and not found_genres:  # Don't override if genre was detected
        print(f"🧠 Semantic/Theme Search Triggered for: {text}")
        semantic_results = semantic_search(text, top_k=5, score_threshold=0.4) # Lower threshold for themes
        if semantic_results:
             return {
                "reply": "Aradığın konuya uygun şunları buldum:",
                "movies": semantic_results
            }

    # 4.3 Title Search (Fallback)
    if len(search_query) > 2:
        title_res = search_title(search_query)
        # Sadece iyi bir eşleşme varsa dön, yoksa Semantic'e veya Recommendation'a bırak
        if title_res:
             return {
                "reply": f"Bunu mu arıyorsun?",
                "movies": [{"id": m.id, "title": m.title, "poster": m.poster_url or m.poster_path} for m in title_res]
            }

    # 5. PERSONAL RECOMMENDATION
    recommendation_keywords = ["öner", "tavsiye", "ne izle", "zevkim", "benim için", "mood"]
    if any(k in text_lower for k in recommendation_keywords):
        if not current_user:
            # Login yoksa popüler filmleri verelim (Action: none, sadece bilgi ve prompt)
            popular = db.query(Movie).order_by(Movie.popularity.desc()).limit(5).all()
            return {
                "reply": "Sana özel zevkine göre öneri yapabilmem için giriş yapmalısın. Ama şimdilik en popüler şu filmlere göz at:",
                "movies": [{"id": m.id, "title": m.title, "poster": m.poster_url or m.poster_path} for m in popular]
            }
        
        # Get user's liked movies
        from app.models.like import Like
        user_likes = db.query(Like).filter(Like.user_id == current_user.id).all()
        
        if user_likes:
            liked_movie_ids = [l.movie_id for l in user_likes]
            liked_movies = db.query(Movie).filter(Movie.id.in_(liked_movie_ids)).all()
            
            # Build a combined profile from liked movies' titles and overviews
            profile_parts = []
            for m in liked_movies[:5]:  # Use top 5 recent likes
                profile_parts.append(m.title)
                if m.overview_tr:
                    profile_parts.append(m.overview_tr[:200])  # First 200 chars
                elif m.overview:
                    profile_parts.append(m.overview[:200])
            
            combined_profile = ". ".join(profile_parts)
            print(f"🎯 User profile for recommendation: {combined_profile[:100]}...")
            
            # Use semantic search with this combined profile
            semantic_recs = semantic_search(combined_profile, top_k=10, score_threshold=0.3)
            
            # Filter out already liked movies
            final_recs = [r for r in semantic_recs if r.get("id") not in liked_movie_ids][:5]
            
            if final_recs:
                # Get liked movie titles for response
                liked_titles = ", ".join([m.title for m in liked_movies[:3]])
                return {
                    "reply": f"'{liked_titles}' gibi beğenilerine göre şunları önerebilirim:",
                    "movies": final_recs
                }
        
        # Fallback to classic recommendation
        recs = recommend_personal(db, current_user.id)
        if not recs:
            recs = db.query(Movie).order_by(Movie.popularity.desc()).limit(5).all()
            
        return {
            "reply": "Senin zevkine göre seçtiklerim:",
            "movies": [{"id": m.id, "title": m.title, "poster": m.poster_url or m.poster_path} for m in recs]
        }

    # 6. OTHER KEYWORDS
    if "rastgele" in text_lower or "şans" in text_lower:
        from sqlalchemy.sql.expression import func
        random_movie = db.query(Movie).order_by(func.random()).first()
        if random_movie:
             return {
                "reply": f"Şansına bu çıktı: {random_movie.title}",
                "movies": [{"id": random_movie.id, "title": random_movie.title, "poster": random_movie.poster_url or random_movie.poster_path}]
            }

    # 7. GENERIC FALLBACK TO SEMANTIC
    # If nothing else worked, try semantic logic one last time with the raw text
    fallback_semantic = semantic_search(text, top_k=3)
    if fallback_semantic:
         return {
            "reply": "Tam anlayamadım ama belki şunlar ilgini çeker:",
            "movies": fallback_semantic
        }

    # 8. KEYWORD FALLBACK (Empty State Handler)
    # User typed something very specific that wasn't found. 
    # Try to find popular movies containing at least one keyword.
    keywords = [w for w in text_lower.split() if len(w) > 3 and w not in stopwords]
    if keywords:
        keyword_filters = [Movie.title.ilike(f"%{kw}%") for kw in keywords]
        keyword_filters += [Movie.overview_tr.ilike(f"%{kw}%") for kw in keywords]
        keyword_filters += [Movie.genres.ilike(f"%{kw}%") for kw in keywords]
        
        keyword_results = (db.query(Movie)
                            .filter(or_(*keyword_filters))
                            .order_by(Movie.popularity.desc())
                            .limit(5).all())
        
        if keyword_results:
            return {
                "reply": f"'{text}' için tam sonuç bulamadım ama şunlara bakabilirsin:",
                "movies": [{"id": m.id, "title": m.title, "poster": m.poster_url or m.poster_path} for m in keyword_results]
            }
    
    # 9. ABSOLUTE FALLBACK - Suggest popular if nothing matched
    popular_fallback = db.query(Movie).order_by(Movie.popularity.desc()).limit(3).all()
    if popular_fallback:
        return {
            "reply": "Aradığını bulamadım, ama en popüler filmlere göz atabilirsin:",
            "movies": [{"id": m.id, "title": m.title, "poster": m.poster_url or m.poster_path} for m in popular_fallback]
        }

    return {
        "reply": "Bunu tam anlayamadım. 'Komedi filmleri', 'Cem Yılmaz', 'Ağlatan filmler' gibi aramalar yapabilirsin.",
        "action": "none"
    }
