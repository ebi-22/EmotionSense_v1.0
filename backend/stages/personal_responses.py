"""
Personal Response Generator - Smart Template-Based
Generates caring, relationship-aware response suggestions.
No external API needed - uses intelligent template matching.
"""

import random
from typing import Dict, List


class PersonalResponseGenerator:
    """
    Generates personal/caring response suggestions for chat.
    Uses smart template selection based on emotion + context.
    """
    
    def __init__(self):
        print("✓ Personal Response Generator loaded")
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load personal response templates."""
        return {
            "sadness": {
                "caring": [
                    "Oh no, what happened? I'm here for you ❤️",
                    "Hey, talk to me. What's going on? 💜",
                    "I can tell something's bothering you. Want to share?",
                    "I'm here to listen. You don't have to go through this alone 🤗",
                    "That doesn't sound good. Are you okay? Tell me everything",
                ],
                "supportive": [
                    "I'm sorry you're feeling this way. I'm right here with you 💪",
                    "Whatever it is, we'll figure it out together",
                    "You've got me. Always. What can I do to help?",
                    "It's okay to not be okay. Let's talk about it",
                ],
                "playful": [
                    "Sending you the biggest virtual hug right now 🫂",
                    "Should I come over with ice cream? 🍦",
                    "Want me to send you cute memes to cheer you up? 😊",
                ]
            },
            "anger": {
                "caring": [
                    "Hey, what happened? Talk to me",
                    "I can tell you're upset. I'm listening ❤️",
                    "That sounds frustrating. Want to vent?",
                    "I'm on your side. Tell me what's going on",
                ],
                "supportive": [
                    "Your feelings are valid. What happened?",
                    "That's totally understandable. I'd be upset too",
                    "I hear you. That does sound really annoying",
                ],
                "playful": [
                    "Okay who do I need to fight? 😤",
                    "Want me to be angry with you? I'm ready! 💪",
                ]
            },
            "fear": {
                "caring": [
                    "Hey, don't worry. I'm right here with you ❤️",
                    "Whatever happens, we'll face it together",
                    "It's okay to be scared. I've got you 🤗",
                    "Take a deep breath. You're not alone in this",
                ],
                "supportive": [
                    "You're stronger than you think. You've got this!",
                    "I believe in you completely. You can handle this 💪",
                    "Remember, you've overcome tough things before",
                ]
            },
            "joy": {
                "caring": [
                    "Yay! That's amazing! Tell me more! 🎉",
                    "I'm so happy for you! 💜",
                    "That's wonderful news! You deserve this!",
                ],
                "supportive": [
                    "You earned this! So proud of you! 🌟",
                    "This is great! Celebrate yourself!",
                ],
                "playful": [
                    "Let's goooo! 🎊",
                    "Party time! This calls for celebration! 🥳",
                ]
            },
            "neutral": {
                "caring": [
                    "Hey, how are you really doing? 💜",
                    "I'm here if you want to talk about anything",
                    "What's on your mind?",
                ],
                "supportive": [
                    "I'm always here for you, you know that right?",
                    "Let me know if there's anything you need",
                ],
                "playful": [
                    "So... what's the tea? ☕",
                    "Tell me more! I want to know everything 😊",
                ]
            },
            "stress": {
                "caring": [
                    "Hey, please don't stress too much. You've got this ❤️",
                    "Take a deep breath. Everything will be okay 💜",
                    "I'm here for you. What's stressing you out?",
                ],
                "supportive": [
                    "You're so capable. Trust yourself!",
                    "You've handled tough things before. You'll get through this too 💪",
                ],
                "playful": [
                    "Stress is just your brain being dramatic. You're amazing! ✨",
                    "Want to take a break and talk? I'm here 😊",
                ]
            },
            "love": {
                "caring": [
                    "Aww, that's so sweet! 💕",
                    "You're the best, you know that? ❤️",
                    "I feel the same way about you 💜",
                ],
                "playful": [
                    "Stop making me blush! 😊",
                    "You're too cute! 🥰",
                ]
            },
            "gratitude": {
                "caring": [
                    "Of course! I'm always here for you ❤️",
                    "You don't need to thank me. That's what I'm here for 💜",
                ],
                "playful": [
                    "Anything for you! 😊",
                    "That's what friends/partners are for! 🤗",
                ]
            }
        }
    
    def generate_suggestions(
        self, 
        emotion: str, 
        message: str,
        conversation_history: List[str] = None,
        tone: str = "caring"
    ) -> List[Dict[str, str]]:
        """
        Generate response suggestions based on detected emotion.
        Uses smart template selection - no external API needed.
        """
        
        # Map similar emotions to template keys
        emotion_map = {
            'fear': 'fear', 'nervousness': 'fear',
            'sadness': 'sadness', 'grief': 'sadness', 
            'disappointment': 'sadness', 'disapproval': 'sadness',
            'anger': 'anger', 'annoyance': 'anger',
            'joy': 'joy', 'amusement': 'joy', 'excitement': 'joy',
            'love': 'love', 'caring': 'love', 'admiration': 'love',
            'gratitude': 'gratitude', 'approval': 'gratitude',
            'neutral': 'neutral', 'confusion': 'neutral',
            'surprise': 'joy', 'curiosity': 'neutral',
        }
        
        template_key = emotion_map.get(emotion, 'neutral')
        emotion_templates = self.templates.get(template_key, self.templates['neutral'])
        
        # Get templates for the requested tone, or fall back to caring
        tone_templates = emotion_templates.get(tone, emotion_templates.get('caring', []))
        
        # Select 3 diverse suggestions
        suggestions = self._select_diverse(tone_templates, 3)
        
        # Emotion emojis
        emojis = {
            'sadness': '💜', 'fear': '🤗', 'anger': '❤️', 
            'joy': '🎉', 'love': '💕', 'gratitude': '😊',
            'neutral': '💬', 'stress': '💪'
        }
        emoji = emojis.get(template_key, '💜')
        
        return [{"text": text, "emoji": emoji, "tone": tone} for text in suggestions]
    
    def _select_diverse(self, templates: List[str], count: int) -> List[str]:
        """Select diverse suggestions."""
        if len(templates) <= count:
            return templates if templates else ["I'm here for you ❤️"]
        
        selected = random.sample(templates, count)
        return selected


# Quick test
if __name__ == "__main__":
    generator = PersonalResponseGenerator()
    
    # Test template-based generation
    print("\n=== Testing Template Generation ===")
    suggestions = generator.generate_suggestions("sadness", "not that much good", tone="caring")
    for s in suggestions:
        print(f"  {s['emoji']} {s['text']}")
