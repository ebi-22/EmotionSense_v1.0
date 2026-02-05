"""
Personal Chat Pipeline
Simplified pipeline for personal/relationship chat assistance.
No RAG, no professional responses - just emotion detection + personal suggestions.
"""

from typing import Dict, Any, List
from .rules import RulesEngine
from .emotion_multilang import MultiLangEmotionClassifier


class PersonalPipeline:
    """
    Lightweight pipeline for personal chat assistance.
    Detects emotions and generates caring/personal response suggestions.
    """
    
    def __init__(self):
        print("Initializing Personal Chat Pipeline...")
        
        # Stage 1: Rules Engine (for crisis detection)
        self.rules_engine = RulesEngine()
        print("✓ Rules Engine loaded")
        
        # Stage 2: Emotion Classifier
        self.emotion_classifier = MultiLangEmotionClassifier()
        print("✓ Emotion Classifier loaded")
        
        print("Personal Pipeline ready!")
    
    def analyze(self, message: str, conversation_history: List[str] = None) -> Dict[str, Any]:
        """
        Analyze a message with optional conversation context.
        
        Args:
            message: The current message to analyze
            conversation_history: List of previous messages for context
        
        Returns:
            Dict with emotion, confidence, context analysis
        """
        # Analyze current message emotion
        emotion_result = self.emotion_classifier.analyze(message)
        
        # Check rules for crisis/urgency
        rules_result = self.rules_engine.analyze(message)
        
        # Override emotion based on rules (for Tanglish/Hinglish)
        final_emotion = emotion_result.get('emotion', 'neutral')
        final_confidence = emotion_result.get('confidence', 0)
        
        rule_flags = rules_result.get('rule_flags', [])
        
        if 'ANGER_DETECTED' in rule_flags:
            final_emotion = 'anger'
            final_confidence = 0.85
        elif 'SADNESS_DETECTED' in rule_flags:
            final_emotion = 'sadness'
            final_confidence = 0.80
        elif 'CRISIS_DETECTED' in rule_flags:
            final_emotion = 'fear'
            final_confidence = 0.99
        elif 'JOY_DETECTED' in rule_flags and final_emotion == 'neutral':
            final_emotion = 'joy'
            final_confidence = max(final_confidence, 0.75)
        
        # Analyze conversation context if provided
        context_mood = self._analyze_context(conversation_history) if conversation_history else None
        
        return {
            "message": message,
            "emotion": final_emotion,
            "confidence": final_confidence,
            "language": emotion_result.get('language', 'english'),
            "is_crisis": rules_result['is_crisis'],
            "urgency": rules_result['urgency'],
            "top_emotions": emotion_result.get('top_5_emotions', [])[:3],
            "context_mood": context_mood,
            "matched_keywords": rules_result.get('matched_keywords', [])
        }
    
    def _analyze_context(self, history: List[str]) -> Dict[str, Any]:
        """
        Analyze conversation history to understand overall mood.
        """
        if not history:
            return None
        
        emotions = []
        for msg in history[-5:]:  # Last 5 messages
            result = self.emotion_classifier.analyze(msg)
            emotions.append(result.get('emotion', 'neutral'))
        
        # Count emotions
        from collections import Counter
        emotion_counts = Counter(emotions)
        dominant_emotion = emotion_counts.most_common(1)[0][0] if emotions else 'neutral'
        
        return {
            "dominant_mood": dominant_emotion,
            "message_count": len(history),
            "recent_emotions": emotions
        }


# Quick test
if __name__ == "__main__":
    pipeline = PersonalPipeline()
    
    test_cases = [
        ("not that much good", ["hi how are you"]),
        ("I'm feeling really sad today", []),
        ("This is so frustrating!!!", ["Why did you do that?"]),
    ]
    
    for message, history in test_cases:
        print(f"\n{'='*50}")
        print(f"Message: {message}")
        print(f"History: {history}")
        result = pipeline.analyze(message, history)
        print(f"Emotion: {result['emotion']} ({result['confidence']*100:.1f}%)")
