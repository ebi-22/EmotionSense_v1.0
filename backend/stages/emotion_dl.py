"""
English-only Emotion Classifier
Wrapper around MultiLangEmotionClassifier for English-only mode.
Uses GoEmotions model for 28-class emotion detection.
"""

from .emotion_multilang import MultiLangEmotionClassifier


class EmotionClassifier(MultiLangEmotionClassifier):
    """
    English-only emotion classifier.
    Inherits all functionality from MultiLangEmotionClassifier
    but optimized for English text only.
    """
    
    def __init__(self):
        """Initialize with English-only mode."""
        super().__init__()
        print("✓ English Emotion Classifier ready")
    
    def analyze(self, text: str):
        """
        Analyze English text for emotions.
        Directly uses GoEmotions without translation/transliteration.
        """
        # Call parent class analyze method
        result = super().analyze(text)
        
        # Override language to english for clarity
        result['language'] = 'english'
        
        return result


# Quick test
if __name__ == "__main__":
    classifier = EmotionClassifier()
    
    test_cases = [
        "I am so happy today!",
        "This is making me angry",
        "I'm worried about the results",
        "Thank you so much for your help!"
    ]
    
    for text in test_cases:
        print(f"\nInput: {text}")
        result = classifier.analyze(text)
        print(f"Emotion: {result['emotion']} ({result['confidence']*100:.1f}%)")
        print(f"Top 5: {result['top_5_emotions'][:3]}")
