// Background Service Worker for EmotionSense Extension
// Handles API communication and message passing

const API_URL = 'http://localhost:5000';

// Message cache to avoid duplicate API calls
const messageCache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'analyzeMessage') {
    handleAnalyzeMessage(request.data, sendResponse);
    return true; // Keep channel open for async response
  } else if (request.action === 'getSettings') {
    handleGetSettings(sendResponse);
    return true;
  } else if (request.action === 'saveSettings') {
    handleSaveSettings(request.data, sendResponse);
    return true;
  }
});

// Analyze message and get suggestions
async function handleAnalyzeMessage(data, sendResponse) {
  const { text, messageId, conversationHistory } = data;

  console.log('[EmotionSense Background] Analyzing message:', text);
  console.log('[EmotionSense Background] Conversation history:', conversationHistory);

  // Check cache first
  const cached = messageCache.get(messageId);
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    console.log('[EmotionSense] Using cached result');
    sendResponse({ success: true, data: cached.data });
    return;
  }

  try {
    // Get settings
    const settings = await chrome.storage.sync.get({
      apiUrl: API_URL,
      tone: 'caring',
      enabled: true
    });

    if (!settings.enabled) {
      sendResponse({ success: false, error: 'Extension disabled' });
      return;
    }

    console.log('[EmotionSense Background] API URL:', settings.apiUrl);
    console.log('[EmotionSense Background] Request payload:', {
      text: text,
      conversation_history: conversationHistory || [],
      source: 'whatsapp_extension',
      tone: settings.tone
    });

    // Call API
    const response = await fetch(`${settings.apiUrl}/suggest`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        text: text,
        conversation_history: conversationHistory || [],
        source: 'whatsapp_extension',
        tone: settings.tone
      })
    });

    console.log('[EmotionSense Background] API response status:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('[EmotionSense Background] API error response:', errorText);
      throw new Error(`API error: ${response.status} - ${errorText}`);
    }

    const result = await response.json();
    console.log('[EmotionSense Background] API result:', result);

    // Validate the response structure
    if (!result.emotion || !result.suggestions) {
      throw new Error('Invalid API response structure');
    }

    // Cache the result
    messageCache.set(messageId, {
      data: result,
      timestamp: Date.now()
    });

    // Clean old cache entries
    cleanCache();

    sendResponse({ success: true, data: result });

  } catch (error) {
    console.error('[EmotionSense] API error:', error);
    
    // Provide fallback response for debugging
    const fallbackResponse = {
      emotion: 'neutral',
      confidence: 0.5,
      urgency: 'low',
      suggestions: [
        { text: "I understand what you're saying", emoji: "💬", tone: "caring" },
        { text: "Thanks for sharing that with me", emoji: "🙏", tone: "caring" },
        { text: "I appreciate you telling me", emoji: "❤️", tone: "caring" }
      ]
    };
    
    console.log('[EmotionSense] Using fallback response due to error');
    sendResponse({ 
      success: true, 
      data: fallbackResponse,
      isError: true,
      error: error.message 
    });
  }
}

// Get settings from storage
async function handleGetSettings(sendResponse) {
  try {
    const settings = await chrome.storage.sync.get({
      apiUrl: API_URL,
      tone: 'caring',
      enabled: true,
      whatsappEnabled: true,
      instagramEnabled: true
    });
    sendResponse({ success: true, data: settings });
  } catch (error) {
    sendResponse({ success: false, error: error.message });
  }
}

// Save settings to storage
async function handleSaveSettings(data, sendResponse) {
  try {
    await chrome.storage.sync.set(data);
    sendResponse({ success: true });
  } catch (error) {
    sendResponse({ success: false, error: error.message });
  }
}

// Clean old cache entries
function cleanCache() {
  const now = Date.now();
  for (const [key, value] of messageCache.entries()) {
    if (now - value.timestamp > CACHE_DURATION) {
      messageCache.delete(key);
    }
  }
}

// Clear cache every 10 minutes
setInterval(cleanCache, 10 * 60 * 1000);

console.log('[EmotionSense] Background service worker initialized');
