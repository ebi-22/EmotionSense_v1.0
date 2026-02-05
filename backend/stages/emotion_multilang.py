"""
Multi-Language Emotion Classifier
Supports: English, Hindi, Tamil, Telugu, Kannada, Malayalam
Uses Translation + GoEmotions for accurate emotion detection.

Models are stored locally in backend/models/
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import re

# Set HuggingFace cache to local folder
MODEL_DIR = Path(__file__).parent.parent / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

os.environ["HF_HOME"] = str(MODEL_DIR)
os.environ["TRANSFORMERS_CACHE"] = str(MODEL_DIR)
os.environ["SENTENCE_TRANSFORMERS_HOME"] = str(MODEL_DIR)

from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer

# GoEmotions model - 28 emotion classes
EMOTION_MODEL = "SamLowe/roberta-base-go_emotions"

# Language detection patterns (native scripts)
INDIC_CHARS = {
    'hindi': '\u0900-\u097F',      # Devanagari
    'tamil': '\u0B80-\u0BFF',      # Tamil
    'telugu': '\u0C00-\u0C7F',     # Telugu
    'kannada': '\u0C80-\u0CFF',    # Kannada
    'malayalam': '\u0D00-\u0D7F',  # Malayalam
}


class MultiLangEmotionClassifier:
    def __init__(self):
        """
        Initialize emotion classifier.
        Uses GoEmotions model stored locally for 28-class emotion detection.
        """
        self.model_dir = MODEL_DIR
        
        print(f"Loading GoEmotions model (28 emotions)...")
        print(f"Model directory: {MODEL_DIR}")
        
        # Check if model exists locally, otherwise download
        local_model_path = MODEL_DIR / "go_emotions"
        
        if local_model_path.exists():
            print(f"Loading from local: {local_model_path}")
            self.classifier = pipeline(
                "text-classification",
                model=str(local_model_path),
                top_k=None,
                device=-1
            )
        else:
            print(f"Downloading model: {EMOTION_MODEL}")
            # Download and save locally
            model = AutoModelForSequenceClassification.from_pretrained(EMOTION_MODEL)
            tokenizer = AutoTokenizer.from_pretrained(EMOTION_MODEL)
            
            # Save locally
            model.save_pretrained(str(local_model_path))
            tokenizer.save_pretrained(str(local_model_path))
            print(f"Model saved to: {local_model_path}")
            
            self.classifier = pipeline(
                "text-classification",
                model=str(local_model_path),
                top_k=None,
                device=-1
            )
        
        print("✓ GoEmotions model loaded!")
    
    def detect_language(self, text: str) -> str:
        """Detect language based on script."""
        for lang, char_range in INDIC_CHARS.items():
            pattern = f'[{char_range}]'
            if re.search(pattern, text):
                if re.search(r'[a-zA-Z]{2,}', text):
                    return f'{lang}_mixed'
                return lang
        return 'english'
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for emotions.
        Flow: Transliterate → Translate → GoEmotions ML
        """
        try:
            original_text = text
            detected_lang = 'english'
            was_translated = False
            
            # Step 1: Transliteration (Romanized → Native script)
            try:
                from .transliterate import smart_transliterate
                transliterated, translit_lang, success = smart_transliterate(text)
                
                if success and translit_lang not in ['english', 'native', 'unknown']:
                    text = transliterated
                    detected_lang = translit_lang
                    print(f"[Transliteration] {translit_lang}: '{original_text}' -> '{text}'")
            except Exception as e:
                print(f"[Transliteration] Skipped: {e}")
            
            # Step 2: Detect language from script
            script_lang = self.detect_language(text)
            if script_lang != 'english':
                detected_lang = script_lang
            
            # Step 3: Translate to English if needed
            if detected_lang != 'english':
                try:
                    translated = self._translate_to_english(text, detected_lang)
                    if translated and translated != text:
                        print(f"[Translation] {detected_lang}: '{text}' -> '{translated}'")
                        text = translated
                        was_translated = True
                except Exception as e:
                    print(f"[Translation] Failed: {e}")
            
            # Step 4: GoEmotions ML analysis
            results = self.classifier(text)
            
            if isinstance(results, list) and len(results) > 0:
                if isinstance(results[0], list):
                    emotions = results[0]
                else:
                    emotions = results
            else:
                return {"error": "Empty model output", "language": detected_lang}
            
            emotions.sort(key=lambda x: x['score'], reverse=True)
            top_emotion = emotions[0]
            
            return {
                "emotion": top_emotion['label'],
                "confidence": round(top_emotion['score'], 4),
                "language": detected_lang,
                "original_text": original_text,
                "translated": was_translated,
                "top_5_emotions": [
                    {"label": e['label'], "score": round(e['score'], 4)}
                    for e in emotions[:5]
                ],
                "all_scores": [
                    {"label": e['label'], "score": round(e['score'], 4)}
                    for e in emotions
                ]
            }
            
        except Exception as e:
            return {"error": str(e), "language": "unknown"}
    
    def _translate_to_english(self, text: str, source_lang: str) -> str:
        """Translate to English using Google Translate API."""
        import requests
        
        lang_codes = {
            'tamil': 'ta', 'hindi': 'hi', 'telugu': 'te',
            'kannada': 'kn', 'malayalam': 'ml', 'bengali': 'bn',
            'tamil_mixed': 'ta', 'hindi_mixed': 'hi'
        }
        
        src = lang_codes.get(source_lang.replace('_romanized', '').replace('_mixed', ''), 'auto')
        
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': src,
                'tl': 'en',
                'dt': 't',
                'q': text
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                result = response.json()
                if result and len(result) > 0 and result[0]:
                    translated = ''.join([part[0] for part in result[0] if part[0]])
                    return translated
        except Exception as e:
            print(f"Translation error: {e}")
        
        return text


# Test
if __name__ == "__main__":
    classifier = MultiLangEmotionClassifier()
    
    test_cases = [
        "I'm so happy today!",
        "I am very angry with you",
        "This makes me sad",
    ]
    
    for text in test_cases:
        print(f"\nInput: {text}")
        result = classifier.analyze(text)
        print(f"Emotion: {result.get('emotion')} ({result.get('confidence', 0)*100:.1f}%)")
