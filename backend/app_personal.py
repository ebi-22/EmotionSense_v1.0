"""
EmotionSense Personal API
FastAPI server for personal chat emotion detection and response suggestions.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add stages to path
sys.path.insert(0, str(Path(__file__).parent))

from stages.pipeline_personal import PersonalPipeline
from stages.personal_responses import PersonalResponseGenerator

# Initialize FastAPI
app = FastAPI(
    title="EmotionSense Personal API",
    description="AI-powered emotion detection for personal chats - WhatsApp & Instagram",
    version="3.0.0"
)

# Enable CORS for browser extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
print("Starting EmotionSense Personal API...")
pipeline = PersonalPipeline()

# Check if AI generation is enabled
use_ai = os.getenv("USE_AI_GENERATION", "true").lower() == "true"
print(f"Response Generation Mode: {'AI (GPT-2)' if use_ai else 'Templates'}")
response_generator = PersonalResponseGenerator(use_ai=use_ai)

print("API Ready!")


# Request/Response Models
class SuggestRequest(BaseModel):
    text: str
    conversation_history: Optional[List[str]] = []
    tone: Optional[str] = "caring"
    source: Optional[str] = "extension"


class Suggestion(BaseModel):
    text: str
    emoji: str
    tone: str


class SuggestResponse(BaseModel):
    emotion: str
    confidence: float
    urgency: str
    is_crisis: bool
    suggestions: List[Suggestion]


# Endpoints
@app.get("/")
def root():
    return {
        "service": "EmotionSense Personal API",
        "version": "3.0.0",
        "status": "running",
        "description": "Personal chat emotion detection & response suggestions",
        "endpoints": {
            "suggest": "POST /suggest - Get response suggestions",
            "health": "GET /health - Check API health"
        }
    }


@app.get("/health")
def health():
    return {"status": "healthy", "mode": "personal"}


@app.post("/suggest", response_model=SuggestResponse)
def suggest_responses(request: SuggestRequest):
    """
    Analyze a message and generate personal response suggestions.
    
    - Detects emotion in the incoming message
    - Uses conversation history for context
    - Returns caring/supportive/playful suggestions
    """
    if not request.text or len(request.text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        # Analyze message with context
        analysis = pipeline.analyze(
            message=request.text,
            conversation_history=request.conversation_history
        )
        
        # Generate personal response suggestions
        suggestions = response_generator.generate_suggestions(
            emotion=analysis['emotion'],
            message=request.text,
            conversation_history=request.conversation_history,
            tone=request.tone or "caring"
        )
        
        return SuggestResponse(
            emotion=analysis['emotion'],
            confidence=analysis['confidence'],
            urgency=analysis['urgency'],
            is_crisis=analysis['is_crisis'],
            suggestions=[Suggestion(**s) for s in suggestions]
        )
        
    except Exception as e:
        print(f"Error in suggest endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# Legacy endpoint for compatibility
@app.post("/analyze")
def analyze(request: SuggestRequest):
    """Legacy analyze endpoint - redirects to suggest."""
    return suggest_responses(request)


# Run with: python app_personal.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
