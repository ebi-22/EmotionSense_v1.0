"""
Personal Response Generator - AI-Powered + Template Fallback
Generates caring, relationship-aware response suggestions using GPT-2.
Falls back to templates if generation fails.
"""

import random
from typing import Dict, List
import os


class PersonalResponseGenerator:
    """
    Generates personal/caring response suggestions for chat.
    Uses GPT-2 for dynamic generation, with template fallback.
    """
    
    def __init__(self, use_ai=True):
        print("Initializing Personal Response Generator...")
        self.use_ai = use_ai
        self.generator = None
        
        # Load AI generator if enabled
        if self.use_ai:
            try:
                from transformers import pipeline
                print("Loading GPT-2 model for text generation...")
                self.generator = pipeline(
                    'text-generation',
                    model='gpt2',
                    device=-1  # CPU
                )
                print("✓ GPT-2 AI Generator loaded!")
            except Exception as e:
                print(f"⚠ GPT-2 loading failed: {e}")
                print("✓ Falling back to template mode")
                self.use_ai = False
        
        # Load templates as fallback
        self.templates = self._load_templates()
        print("✓ Personal Response Generator ready!")
    
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
        Uses GPT-2 AI generation with template fallback.
        """
        
        # Emotion emoji mapping
        emojis = {
            'sadness': '💜', 'fear': '🤗', 'anger': '❤️', 
            'joy': '🎉', 'love': '💕', 'gratitude': '😊',
            'neutral': '💬', 'stress': '💪'
        }
        
        # Map similar emotions
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
        emoji = emojis.get(template_key, '💜')
        
        # Try AI generation first
        if self.use_ai and self.generator:
            try:
                suggestions = self._generate_with_ai(message, emotion, tone, conversation_history)
                if suggestions:
                    return [{"text": text, "emoji": emoji, "tone": tone} for text in suggestions]
            except Exception as e:
                print(f"AI generation failed: {e}, using templates")
        
        # Fallback to templates
        emotion_templates = self.templates.get(template_key, self.templates['neutral'])
        tone_templates = emotion_templates.get(tone, emotion_templates.get('caring', []))
        suggestions = self._select_diverse(tone_templates, 3)
        
        return [{"text": text, "emoji": emoji, "tone": tone} for text in suggestions]
    
    def _generate_with_ai(self, message: str, emotion: str, tone: str, history: List[str] = None) -> List[str]:
        """Generate responses using GPT-2 with improved prompting."""
        
        # Emotion-specific response starters for better generation
        starters = {
            "sadness": ["I'm so sorry", "I'm here", "That must be", "I understand", "Oh no"],
            "fear": ["Don't worry", "You're safe", "I'm right here", "Everything will be", "Take a breath"],
            "anger": ["I hear you", "That's frustrating", "I understand", "You have every right", "I'm listening"],
            "joy": ["That's amazing", "I'm so happy", "Wonderful", "Congratulations", "That's fantastic"],
            "stress": ["I know it's", "You've got this", "Take it easy", "You're doing great", "Breathe"],
            "love": ["That's sweet", "I feel", "You're wonderful", "Thank you", "Love you"],
            "neutral": ["I hear you", "Tell me more", "I'm listening", "That's interesting", "I understand"]
        }
        
        # Get appropriate starters
        emotion_starters = starters.get(emotion, starters["neutral"])
        
        # Build better examples in prompt (few-shot learning)
        examples = {
            "caring": 'Message: "I failed my test"\nReply: "Oh no, I\'m so sorry. But one test doesn\'t define you. I\'m here for you ❤️"\n\n',
            "supportive": 'Message: "I\'m nervous about tomorrow"\nReply: "You\'ve prepared well and you\'re capable. I believe in you! You\'ve got this! 💪"\n\n',
            "playful": 'Message: "I\'m bored"\nReply: "Boredom emergency! Should we have a virtual dance party or watch cat videos? 😄"\n\n',
            "formal": 'Message: "I need help"\nReply: "I would be happy to assist you. Please let me know what you need."\n\n'
        }
        
        example = examples.get(tone, examples["caring"])
        
        # Create better structured prompt
        prompt = f"{example}Message: \"{message}\"\nReply:"
        
        # Generate responses with better parameters
        responses = []
        for i in range(3):
            try:
                # Use different starter for each generation
                starter = emotion_starters[i % len(emotion_starters)]
                custom_prompt = f"{prompt} {starter}"
                
                result = self.generator(
                    custom_prompt,
                    max_length=len(custom_prompt.split()) + 25,  # Limit to ~25 new words
                    min_length=len(custom_prompt.split()) + 8,   # At least 8 new words
                    num_return_sequences=1,
                    temperature=0.7,  # Lower temperature for more coherent text
                    do_sample=True,
                    top_k=50,
                    top_p=0.92,
                    repetition_penalty=1.2,  # Reduce repetition
                    no_repeat_ngram_size=3,  # Avoid repeating 3-grams
                    pad_token_id=50256,
                    eos_token_id=50256
                )
                
                # Extract and clean response
                generated = result[0]['generated_text']
                response = generated.replace(custom_prompt, "").replace(prompt, "").strip()
                
                # Clean up the response
                response = response.split('\n')[0].strip()  # First line only
                response = response.split('. ')[0] + '.'    # First sentence
                response = response.replace('..', '.')
                
                # Validate response quality
                if (len(response) > 15 and len(response) < 150 and 
                    not response.startswith('Message:') and 
                    not response.startswith('Reply:')):
                    responses.append(response)
                    
            except Exception as e:
                print(f"Generation attempt {i+1} failed: {e}")
                continue
        
        # If generation failed, return None to use templates
        return responses if len(responses) >= 2 else None
    
    def _select_diverse(self, templates: List[str], count: int) -> List[str]:
        """Select diverse suggestions."""
        if len(templates) <= count:
            return templates if templates else ["I'm here for you ❤️"]
        
        selected = random.sample(templates, count)
        return selected


# Quick test
if __name__ == "__main__":
    generator = PersonalResponseGenerator(use_ai=True)
    
    # Test AI generation
    print("\n=== Testing AI-Generated Responses ===")
    suggestions = generator.generate_suggestions("sadness", "I'm feeling really down today", tone="caring")
    for i, s in enumerate(suggestions, 1):
        print(f"  {i}. {s['emoji']} {s['text']}")
    
    print("\n=== Testing Another Example ===")
    suggestions = generator.generate_suggestions("stress", "I'm so stressed about my exams", tone="supportive")
    for i, s in enumerate(suggestions, 1):
        print(f"  {i}. {s['emoji']} {s['text']}")

