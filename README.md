# EmotionSense - Multi-Language Emotion Detection

A production-ready emotion detection system with support for Indian languages.

## Features

- **28 Emotion Classes**: anger, joy, sadness, fear, love, caring, desire, etc.
- **Multi-Language**: Tamil, Hindi, Telugu, Kannada, Malayalam
- **Code-Mixed**: Tanglish, Hinglish (Romanized Indian languages)
- **Crisis Detection**: Real-time safety alerts
- **RAG**: Similar case retrieval
- **Professional Dashboard**: Ready-to-use UI

## Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python app.py
```

**First run will download the GoEmotions model (~500MB) to `models/` directory.**

## Usage

Open `test_page/index.html` in browser.

API: `http://localhost:5000/analyze`

## Tested Examples

| Input | Detected |
|-------|----------|
| `naan kovama iruken` | anger 82% |
| `I am very happy` | joy 95% |
| `vendikitten saami kitta...` | caring 82% |

## Project Structure

```
emosense/
├── backend/
│   ├── app.py              # FastAPI server
│   ├── requirements.txt
│   ├── data/
│   │   ├── rules.json      # Crisis/urgency keywords
│   │   └── cases.jsonl     # Sample cases for RAG
│   ├── models/             # Auto-downloaded models
│   └── stages/
│       ├── emotion_multilang.py  # Main classifier
│       ├── transliterate.py      # Romanized → Native
│       ├── pipeline.py           # Orchestrator
│       ├── rules.py              # Crisis detection
│       ├── rag.py                # Similar case search
│       ├── llm.py                # Response generation
│       └── sqlite_logger.py      # Audit logging
└── test_page/
    └── index.html          # Dashboard UI
```
