# EmotionSense Browser Extension

AI-powered empathetic response suggestions for WhatsApp Web and Instagram DMs.

## Features

- 🎯 **Real-time Emotion Detection**: Analyzes incoming messages and detects 28 different emotions
- 💬 **Smart Suggestions**: Provides 3 empathetic response suggestions for each message
- 🎨 **Multiple Tones**: Choose from Caring, Supportive, Playful, or Formal response styles
- ⚡ **One-Click Insert**: Insert suggestions directly into chat with a single click
- 🔒 **Privacy-First**: All processing happens locally, no data sent to external servers
- 🌐 **Multi-Platform**: Works on WhatsApp Web and Instagram DMs

## Installation

### 1. Start the Backend Server

First, make sure the EmotionSense backend is running:

```bash
cd backend
.\venv\Scripts\activate
$env:EMOSENSE_MULTILANG="true"
py app.py
```

The server should be running on `http://localhost:5000`

### 2. Load Extension in Chrome/Edge

1. Open Chrome or Edge browser
2. Navigate to `chrome://extensions/` (or `edge://extensions/`)
3. Enable "Developer mode" (toggle in top-right corner)
4. Click "Load unpacked"
5. Select the `extension` folder from this project
6. The EmotionSense icon should appear in your extensions toolbar

## Usage

### WhatsApp Web

1. Open [WhatsApp Web](https://web.whatsapp.com/)
2. Start a conversation
3. When your chat partner sends a message, the extension will:
   - Detect the emotion (stress, sadness, joy, etc.)
   - Show a floating suggestion panel
   - Display 3 empathetic response suggestions
4. Click "Insert" to add a suggestion to your chat input
5. Edit if needed and send!

### Instagram DMs

1. Open [Instagram](https://www.instagram.com/) and go to Messages
2. Open a conversation
3. The extension works the same way as WhatsApp Web

## Settings

Click the EmotionSense icon in your toolbar to access settings:

- **Enable/Disable Extension**: Turn the extension on or off
- **Platform Settings**: Enable/disable for WhatsApp or Instagram individually
- **Response Tone**: Choose your preferred tone:
  - 💜 **Caring & Loving**: Warm, affectionate responses
  - 🤗 **Supportive & Encouraging**: Motivational, uplifting responses
  - 😊 **Playful & Light**: Fun, casual responses
  - 👔 **Formal & Respectful**: Professional, polite responses
- **API Server URL**: Configure the backend server URL (default: `http://localhost:5000`)

## Example

**Scenario**: Your girlfriend sends: "I'm so stressed about my exams 😰"

**Extension Detects**: Stress (87% confidence)

**Suggestions Appear**:
1. 💜 "Oh dear, please don't stress out! You've got this, and I believe in you ❤️"
2. 🤗 "I know exams can be overwhelming, but you're so smart and prepared. Take a deep breath!"
3. 😊 "Hey, remember you've aced tougher things before. Want to take a study break and talk?"

**You Click**: "Insert" on suggestion #1

**Result**: The text appears in your chat input, ready to send!

## Supported Emotions

The extension can detect and respond to:
- Stress, Fear, Anxiety
- Sadness, Grief, Disappointment
- Anger, Annoyance, Frustration
- Joy, Excitement, Love
- Gratitude, Caring, Admiration
- Confusion, Curiosity, Surprise
- And 16 more emotions!

## Privacy & Security

- ✅ All emotion analysis happens on your local machine
- ✅ No data is sent to external servers
- ✅ Messages are not stored permanently
- ✅ You have full control over when to use suggestions

## Troubleshooting

### Extension not working?

1. **Check backend server**: Make sure `http://localhost:5000/health` returns a response
2. **Reload extension**: Go to `chrome://extensions/` and click the reload icon
3. **Check console**: Right-click extension icon → Inspect popup → Check for errors
4. **Refresh page**: Reload WhatsApp Web or Instagram

### Suggestions not appearing?

1. Make sure the extension is enabled in settings
2. Check that the platform (WhatsApp/Instagram) is enabled
3. Verify the message is from your chat partner (not from you)
4. Check browser console for errors (F12)

## Browser Compatibility

- ✅ **Chrome**: Full support
- ✅ **Edge**: Full support (Chromium-based)
- ⚠️ **Firefox**: Requires manifest adjustments
- ⚠️ **Safari**: Requires conversion to Safari extension format

## Future Enhancements

- 🧠 Learning mode: Adapt to your texting style
- 🌍 Multi-language: Respond in detected language
- ⌨️ Keyboard shortcuts: Quick access (Ctrl+1, Ctrl+2, etc.)
- 🎭 Emoji suggestions: Recommend relevant emojis
- 💾 Context awareness: Consider previous messages

## Credits

Built with ❤️ using:
- **GoEmotions** (28-class emotion detection)
- **FastAPI** (Backend API)
- **Chrome Extension Manifest V3**

---

**Version**: 1.0.0  
**License**: MIT  
**Author**: EmotionSense Team
