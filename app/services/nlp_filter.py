from better_profanity import profanity


profanity.load_censor_words()


custom_bad_words = [
    "aptal", "salak", "gerizekalı", "mal", "bok","öküz", "yavşak", "piç", "amk", "aq", "sik", "siktir"
]
profanity.add_censor_words(custom_bad_words)

def is_clean(text: str) -> bool:
    
    return not profanity.contains_profanity(text)

def clean_text(text: str) -> str:
    
    return profanity.censor(text)
