"""
Transliteration Module
Converts Romanized Indian languages to native scripts.
Uses Google's free transliteration API.

Supports: Tamil, Hindi, Telugu, Kannada, Malayalam
"""

import requests
import re
from typing import Tuple, Optional

# Google Input Tools API (free, no key needed)
GOOGLE_TRANSLIT_URL = "https://inputtools.google.com/request"

# Language codes for transliteration
LANG_CODES = {
    'tamil': 'ta-t-i0-und',
    'hindi': 'hi-t-i0-und', 
    'telugu': 'te-t-i0-und',
    'kannada': 'kn-t-i0-und',
    'malayalam': 'ml-t-i0-und',
    'bengali': 'bn-t-i0-und',
    'marathi': 'mr-t-i0-und',
    'gujarati': 'gu-t-i0-und'
}

# Common words that indicate language (for detection)
LANG_INDICATORS = {
    'tamil': ['da', 'pa', 'ma', 'la', 'na', 'ya', 'enna', 'naan', 'avan', 'aval', 'ivan', 'ival', 
              'kovam', 'sogam', 'sandhosham', 'romba', 'semma', 'thala', 'poda', 'podi'],
    'hindi': ['hai', 'hoon', 'kya', 'mein', 'tum', 'aap', 'bahut', 'bohot', 'accha', 'bura', 
              'gussa', 'khushi', 'dukh', 'pyaar', 'nafrat', 'yaar', 'bhai', 'yeh', 'woh'],
    'malayalam': ['alle', 'aanu', 'illa', 'und', 'enthu', 'njan', 'ningal', 'avan', 'aval',
                  'mathi', 'pore', 'kollam'],
    'telugu': ['ra', 'raa', 'andi', 'emi', 'nenu', 'nuvvu', 'vaadu', 'aamey', 'bagundi',
               'chala', 'manchidi', 'kastam']
}


def detect_romanized_language(text: str) -> Optional[str]:
    """
    Detect which Indian language the Romanized text might be.
    Returns language code or None if unclear.
    """
    text_lower = text.lower()
    words = set(re.findall(r'\b\w+\b', text_lower))
    
    scores = {}
    for lang, indicators in LANG_INDICATORS.items():
        score = sum(1 for ind in indicators if ind in words or ind in text_lower)
        if score > 0:
            scores[lang] = score
    
    if not scores:
        return None
    
    # Return language with highest score
    return max(scores, key=scores.get)


def transliterate(text: str, target_lang: str = 'tamil') -> Tuple[str, bool]:
    """
    Transliterate Romanized text to native script.
    Returns (transliterated_text, success_flag)
    """
    if target_lang not in LANG_CODES:
        return text, False
    
    try:
        params = {
            'text': text,
            'itc': LANG_CODES[target_lang],
            'num': 1,
            'cp': 0,
            'cs': 1,
            'ie': 'utf-8',
            'oe': 'utf-8',
            'app': 'demopage'
        }
        
        response = requests.get(GOOGLE_TRANSLIT_URL, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data[0] == 'SUCCESS' and len(data) > 1:
                # Extract transliterated words
                results = data[1]
                transliterated_words = []
                
                for item in results:
                    if len(item) > 1 and len(item[1]) > 0:
                        # Get the first (best) suggestion
                        transliterated_words.append(item[1][0])
                    else:
                        # Keep original if no transliteration found
                        transliterated_words.append(item[0])
                
                result = ' '.join(transliterated_words)
                return result, True
        
        return text, False
        
    except Exception as e:
        print(f"Transliteration error: {e}")
        return text, False


def smart_transliterate(text: str) -> Tuple[str, str, bool]:
    """
    Detect language and transliterate automatically.
    Returns (transliterated_text, detected_language, success_flag)
    """
    # First, check if text contains any Indic script already
    indic_pattern = r'[\u0900-\u0D7F]'  # Covers Devanagari to Malayalam
    if re.search(indic_pattern, text):
        # Already in native script, no transliteration needed
        return text, 'native', True
    
    # Check if mostly English
    english_words = set(['i', 'am', 'is', 'are', 'the', 'a', 'an', 'this', 'that', 'my', 'your',
                         'what', 'how', 'why', 'when', 'where', 'who', 'can', 'will', 'would',
                         'should', 'could', 'have', 'has', 'had', 'do', 'does', 'did', 'be'])
    words = set(re.findall(r'\b\w+\b', text.lower()))
    english_overlap = len(words & english_words)
    
    if english_overlap > len(words) * 0.5:
        # Mostly English, skip transliteration
        return text, 'english', True
    
    # Detect language
    detected = detect_romanized_language(text)
    
    if detected:
        transliterated, success = transliterate(text, detected)
        return transliterated, detected, success
    
    return text, 'unknown', False


# Test
if __name__ == "__main__":
    test_cases = [
        ("naan kovama iruken", "tamil"),
        ("mujhe bahut gussa hai", "hindi"),
        ("enna da pandra", "tamil"),
        ("I am very angry", "english"),
        ("yeh service bakwas hai", "hindi"),
    ]
    
    for text, expected in test_cases:
        result, lang, success = smart_transliterate(text)
        print(f"\nInput: {text}")
        print(f"Detected: {lang}, Success: {success}")
        print(f"Output: {result}")
