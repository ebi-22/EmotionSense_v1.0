// Content Script for WhatsApp Web
// Detects incoming messages and displays suggestion panel

console.log('[EmotionSense] WhatsApp content script loaded');

// Configuration with modern WhatsApp Web selectors (2026)
const CONFIG = {
    // Updated selectors for current WhatsApp Web structure
    messageSelectors: [
        // New structure selectors (2025-2026)
        'div[data-pre-plain-text] div[role="row"]',  // Modern message rows
        'div.message-in',                              // Legacy incoming messages  
        'div[data-id*="false_"]',                     // Messages with false prefix
        'div[aria-label*="Message"]',                 // Accessibility label messages
        'div._21Ahp',                                  // Common message container class
        'div._3_7SH',                                  // Alternative message class
        '[role="row"]',                               // Generic row elements
        'div[data-testid="conversation-panel-messages"] > div > div' // Direct message containers
    ],
    // Multiple text extraction strategies
    textSelectors: [
        'span.selectable-text[dir="ltr"]',            // Primary text content
        'span.selectable-text',                        // Alternative text content  
        'span[data-testid="conversation-text"]',      // Test ID based selector
        'span._11JPr',                                 // Common text span class
        'span._3EFkT',                                 // Alternative text class
        'div._22Msk span',                            // Text within message div
        '.copyable-text span',                         // Copyable text spans
        'span[dir="auto"]',                          // Auto-direction text spans
        '[data-pre-plain-text] span'                  // Text within pre-plain containers
    ],
    // Multiple input selector strategies
    inputSelectors: [
        'div[contenteditable="true"][data-testid="conversation-compose-box-input"]',
        'div[contenteditable="true"][role="textbox"]',
        'footer div[contenteditable="true"]',
        'div[data-testid="compose-box"] div[contenteditable="true"]',
        'div._3uMse[contenteditable="true"]',         // Common compose box class
        'div._1awRl div[contenteditable="true"]'     // Alternative compose container
    ],
    checkInterval: 1500,  // Slightly longer interval to reduce CPU usage
    debug: true           // Enable detailed console logging
};

// State
let lastProcessedMessage = null;
let suggestionPanel = null;
let conversationHistory = [];  // Track recent messages for context
const MAX_HISTORY = 10;  // Keep last 10 messages for context

// Initialize
// Original init function updated to match enhanced version
function init() {
    enhancedInit();
}

// Create persistent floating launcher button
function createFloatingLauncher() {
    // Remove existing if any
    const existing = document.querySelector('.emotionsense-launcher');
    if (existing) existing.remove();

    const launcher = document.createElement('div');
    launcher.className = 'emotionsense-launcher';
    launcher.innerHTML = '<span class="emotionsense-launcher-icon">💜</span>';
    launcher.title = 'EmotionSense is active';

    // Add click handler to toggle last suggestion or show status
    launcher.addEventListener('click', () => {
        if (suggestionPanel) {
            // Toggle visibility of the panel
            if (suggestionPanel.classList.contains('emotionsense-hidden')) {
                showSuggestionPanel();
                showToast('Ready to detect emotions! ⚡');
            } else {
                hideSuggestionPanel();
            }
        }
    });

    document.body.appendChild(launcher);
}

// Monitor for new incoming messages with comprehensive detection
function startMessageMonitoring() {
    console.log('[EmotionSense] Starting enhanced message monitoring...');
    
    if (CONFIG.debug) {
        console.log('[EmotionSense] Available selectors:', CONFIG.messageSelectors);
    }

    setInterval(() => {
        if (CONFIG.debug && Math.random() < 0.1) { // Debug every ~10 iterations
            console.log('[EmotionSense] Scanning for messages...');
        }
        
        // Try to find messages using all selector strategies
        let messages = [];
        let selectorUsed = null;
        
        for (const selector of CONFIG.messageSelectors) {
            try {
                const found = document.querySelectorAll(selector);
                if (found.length > 0) {
                    messages = Array.from(found);
                    selectorUsed = selector;
                    if (CONFIG.debug && Math.random() < 0.05) {
                        console.log(`[EmotionSense] Found ${found.length} messages using: ${selector}`);
                    }
                    break;
                }
            } catch (error) {
                console.warn(`[EmotionSense] Selector failed: ${selector}`, error);
            }
        }

        if (messages.length === 0) {
            if (CONFIG.debug && Math.random() < 0.02) {
                console.log('[EmotionSense] No messages found with current selectors');
                // Debug: show what elements are actually available
                const chatElements = document.querySelectorAll('[data-testid*="conversation"], [role="main"] div');
                console.log('[EmotionSense] Chat elements found:', chatElements.length);
            }
            return;
        }

        // Filter to only incoming messages (exclude outgoing)
        const incomingMessages = messages.filter(msg => {
            // Multiple strategies to identify incoming vs outgoing messages
            const isOutgoing = msg.classList.contains('message-out') || 
                             msg.closest('.message-out') ||
                             msg.querySelector('[data-testid="tail-out"]') ||
                             msg.classList.contains('_3j7s9');
            return !isOutgoing;
        });

        if (incomingMessages.length === 0) return;

        // Get the last incoming message
        const lastMessage = incomingMessages[incomingMessages.length - 1];

        // Extract message text using multiple strategies
        let messageText = extractMessageText(lastMessage);
        
        if (!messageText || messageText.length < 2) {
            if (CONFIG.debug) {
                console.log('[EmotionSense] No valid text extracted from message');
            }
            return;
        }

        // Generate a unique ID for this message
        let messageId = generateMessageId(lastMessage, messageText);

        // Skip if already processed
        if (messageId === lastProcessedMessage) return;

        // Log for debugging
        console.log('[EmotionSense] New message detected:', messageText);
        if (CONFIG.debug) {
            console.log('[EmotionSense] Message ID:', messageId);
            console.log('[EmotionSense] Selector used:', selectorUsed);
        }

        // Process the message
        lastProcessedMessage = messageId;
        processMessage(messageText, messageId);

    }, CONFIG.checkInterval);
}

// Extract text content from message element using multiple strategies
function extractMessageText(messageElement) {
    if (!messageElement) return '';
    
    let text = '';
    
    // Try each text selector strategy
    for (const selector of CONFIG.textSelectors) {
        try {
            const textElements = messageElement.querySelectorAll(selector);
            if (textElements.length > 0) {
                // Combine text from all matching elements
                text = Array.from(textElements)
                    .map(el => el.textContent || el.innerText)
                    .filter(t => t && t.trim())
                    .join(' ')
                    .trim();
                
                if (text.length > 0) {
                    if (CONFIG.debug) {
                        console.log(`[EmotionSense] Text extracted using: ${selector}`);
                    }
                    break;
                }
            }
        } catch (error) {
            console.warn(`[EmotionSense] Text extraction failed for: ${selector}`, error);
        }
    }
    
    // Fallback: try getting text from the entire message element
    if (!text) {
        const fallbackText = messageElement.textContent || messageElement.innerText || '';
        // Clean up common metadata patterns
        text = fallbackText
            .replace(/\d{1,2}:\d{2}\s?(AM|PM)?/gi, '') // Remove timestamps
            .replace(/\n+/g, ' ')                        // Replace newlines with spaces
            .replace(/\s+/g, ' ')                       // Normalize spaces
            .trim();
        
        if (CONFIG.debug && text) {
            console.log('[EmotionSense] Used fallback text extraction');
        }
    }
    
    return text;
}

// Generate unique message ID
function generateMessageId(messageElement, messageText) {
    // Try to get WhatsApp's internal message ID
    let id = messageElement.getAttribute('data-id') ||
             messageElement.getAttribute('data-message-id') ||
             messageElement.closest('[data-id]')?.getAttribute('data-id');
    
    if (!id) {
        // Generate ID based on text content and timestamp
        const timestamp = Date.now();
        const textHash = messageText.substring(0, 20).replace(/[^a-zA-Z0-9]/g, '');
        id = `msg_${textHash}_${timestamp}`;
    }
    
    return id;
}

// Process incoming message
async function processMessage(text, messageId) {
    console.log('[EmotionSense] Processing message:', text);
    console.log('[EmotionSense] Message ID:', messageId);

    // Add to conversation history
    conversationHistory.push(text);
    if (conversationHistory.length > MAX_HISTORY) {
        conversationHistory.shift();  // Remove oldest
    }
    console.log('[EmotionSense] Conversation history:', conversationHistory);

    // Show loading state
    showSuggestionPanel('loading');

    // Send to background script for analysis with conversation context
    chrome.runtime.sendMessage({
        action: 'analyzeMessage',
        data: { 
            text, 
            messageId,
            conversationHistory: conversationHistory.slice(0, -1)  // All except current
        }
    }, (response) => {
        console.log('[EmotionSense] Response from background:', response);
        
        if (response && response.success) {
            if (response.isError) {
                console.warn('[EmotionSense] Using fallback due to API error:', response.error);
                showToast('⚠️ API Error - Using fallback suggestions');
            }
            displaySuggestions(response.data);
        } else {
            console.error('[EmotionSense] Analysis failed:', response?.error);
            
            // Show error-specific fallback
            const errorFallback = {
                emotion: 'neutral',
                confidence: 0.5,
                suggestions: [
                    { text: "I'm here to listen", emoji: "👂", tone: "caring" },
                    { text: "Tell me more about that", emoji: "💭", tone: "caring" },
                    { text: "That sounds important", emoji: "💫", tone: "caring" }
                ]
            };
            
            displaySuggestions(errorFallback);
            showToast('❌ Connection error - using offline suggestions');
        }
    });
}

// Create suggestion panel UI
function createSuggestionPanel() {
    suggestionPanel = document.createElement('div');
    suggestionPanel.id = 'emotionsense-panel';
    suggestionPanel.className = 'emotionsense-hidden';
    suggestionPanel.innerHTML = `
    <div class="emotionsense-header">
      <div class="emotionsense-emotion">
        <span class="emotionsense-icon">💬</span>
        <span class="emotionsense-label">Analyzing...</span>
      </div>
      <button class="emotionsense-close" title="Close">×</button>
    </div>
    <div class="emotionsense-suggestions">
      <div class="emotionsense-loading">
        <div class="emotionsense-spinner"></div>
        <p>Getting suggestions...</p>
      </div>
    </div>
  `;

    document.body.appendChild(suggestionPanel);

    // Add close button listener
    suggestionPanel.querySelector('.emotionsense-close').addEventListener('click', () => {
        hideSuggestionPanel();
    });
}

// Show suggestion panel
function showSuggestionPanel(state = 'visible') {
    if (!suggestionPanel) return;

    suggestionPanel.className = state === 'loading'
        ? 'emotionsense-visible emotionsense-loading-state'
        : 'emotionsense-visible';
}

// Hide suggestion panel
function hideSuggestionPanel() {
    if (!suggestionPanel) return;
    suggestionPanel.className = 'emotionsense-hidden';
}

// Display suggestions
function displaySuggestions(data) {
    if (!suggestionPanel) return;

    const { emotion, confidence, suggestions } = data;

    // Update emotion display
    const emotionIcon = getEmotionIcon(emotion);
    const emotionLabel = `${emotion.charAt(0).toUpperCase() + emotion.slice(1)} (${Math.round(confidence * 100)}%)`;

    suggestionPanel.querySelector('.emotionsense-icon').textContent = emotionIcon;
    suggestionPanel.querySelector('.emotionsense-label').textContent = emotionLabel;

    // Create suggestion cards
    const suggestionsHTML = suggestions.map((suggestion, index) => `
    <div class="emotionsense-card">
      <div class="emotionsense-card-text">${suggestion.emoji} ${suggestion.text}</div>
      <div class="emotionsense-card-actions">
        <button class="emotionsense-btn emotionsense-btn-copy" data-index="${index}">
          📋 Copy
        </button>
        <button class="emotionsense-btn emotionsense-btn-insert" data-index="${index}">
          ✏️ Insert
        </button>
      </div>
    </div>
  `).join('');

    suggestionPanel.querySelector('.emotionsense-suggestions').innerHTML = suggestionsHTML;

    // Add button listeners
    suggestionPanel.querySelectorAll('.emotionsense-btn-copy').forEach(btn => {
        btn.addEventListener('click', () => {
            const index = parseInt(btn.getAttribute('data-index'));
            copyToClipboard(suggestions[index].text);
        });
    });

    suggestionPanel.querySelectorAll('.emotionsense-btn-insert').forEach(btn => {
        btn.addEventListener('click', () => {
            const index = parseInt(btn.getAttribute('data-index'));
            insertIntoChat(suggestions[index].text);
        });
    });

    showSuggestionPanel('visible');

    // Auto-hide after 15 seconds
    setTimeout(() => {
        hideSuggestionPanel();
    }, 15000);
}

// Copy text to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        console.log('[EmotionSense] Copied to clipboard');
        // Show brief feedback
        showToast('Copied to clipboard!');
    });
}

// Insert text into chat input with enhanced compatibility
function insertIntoChat(text) {
    let inputBox = null;
    
    // Try multiple input selector strategies
    for (const selector of CONFIG.inputSelectors) {
        try {
            inputBox = document.querySelector(selector);
            if (inputBox) {
                if (CONFIG.debug) {
                    console.log(`[EmotionSense] Found input using: ${selector}`);
                }
                break;
            }
        } catch (error) {
            console.warn(`[EmotionSense] Input selector failed: ${selector}`, error);
        }
    }
    
    if (!inputBox) {
        console.error('[EmotionSense] Chat input not found with any selector');
        if (CONFIG.debug) {
            // Debug: Show available input-like elements
            const possibleInputs = document.querySelectorAll('[contenteditable], input, textarea');
            console.log('[EmotionSense] Available editable elements:', possibleInputs.length);
        }
        showToast('❌ Could not find chat input');
        return;
    }

    try {
        // Clear existing content first
        inputBox.textContent = '';
        inputBox.innerHTML = '';
        
        // Set the new text
        inputBox.textContent = text;
        
        // Create and dispatch multiple events to ensure WhatsApp detects the change
        const events = [
            new Event('focus', { bubbles: true }),
            new Event('input', { bubbles: true, cancelable: true }),
            new Event('keyup', { bubbles: true, cancelable: true }),
            new Event('change', { bubbles: true, cancelable: true }),
            new Event('paste', { bubbles: true, cancelable: true })
        ];
        
        events.forEach(event => {
            try {
                inputBox.dispatchEvent(event);
            } catch (e) {
                console.warn('[EmotionSense] Event dispatch failed:', e);
            }
        });
        
        // Focus the input and position cursor at end
        inputBox.focus();
        
        // Move cursor to end of text
        if (window.getSelection && document.createRange) {
            const range = document.createRange();
            range.selectNodeContents(inputBox);
            range.collapse(false);
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
        }
        
        // Hide panel
        hideSuggestionPanel();
        
        showToast('✅ Text inserted into chat!');
        
        if (CONFIG.debug) {
            console.log('[EmotionSense] Successfully inserted text:', text);
        }
        
    } catch (error) {
        console.error('[EmotionSense] Error inserting text:', error);
        showToast('❌ Failed to insert text');
    }
}

// Show toast notification
function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'emotionsense-toast';
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('emotionsense-toast-show');
    }, 10);

    setTimeout(() => {
        toast.classList.remove('emotionsense-toast-show');
        setTimeout(() => toast.remove(), 300);
    }, 2000);
}

// Get emotion icon
function getEmotionIcon(emotion) {
    const icons = {
        'anger': '😠', 'fear': '😰', 'sadness': '😢', 'joy': '😄',
        'love': '❤️', 'surprise': '😲', 'disgust': '🤢', 'stress': '😓',
        'excitement': '🎉', 'gratitude': '🙏', 'caring': '🤗', 'confusion': '😕',
        'neutral': '😐', 'annoyance': '😒', 'disappointment': '😞'
    };
    return icons[emotion] || '💬';
}

// Enhanced initialization with comprehensive debugging
function enhancedInit() {
    console.log('[EmotionSense] WhatsApp content script loaded v2.0');
    
    // Debug: Log current page info
    if (CONFIG.debug) {
        console.log('[EmotionSense] URL:', window.location.href);
        console.log('[EmotionSense] User agent:', navigator.userAgent);
        console.log('[EmotionSense] Page title:', document.title);
    }
    
    // Check if we're actually on WhatsApp Web
    if (!window.location.hostname.includes('web.whatsapp.com')) {
        console.warn('[EmotionSense] Not on WhatsApp Web, extension may not work properly');
    }
    
    try {
        // Create the persistent floating launcher
        createFloatingLauncher();
        console.log('[EmotionSense] ✓ Floating launcher created');
        
        // Create suggestion panel
        createSuggestionPanel();
        console.log('[EmotionSense] ✓ Suggestion panel created');
        
        // Start monitoring for new messages
        startMessageMonitoring();
        console.log('[EmotionSense] ✓ Message monitoring started');
        
        // Debug: Check initial page state
        if (CONFIG.debug) {
            setTimeout(() => {
                console.log('[EmotionSense] Page scan after 3 seconds:');
                const messages = document.querySelectorAll(CONFIG.messageSelectors[0]);
                console.log('[EmotionSense] Messages found:', messages.length);
                
                const inputs = document.querySelectorAll(CONFIG.inputSelectors[0]);
                console.log('[EmotionSense] Input boxes found:', inputs.length);
                
                if (messages.length === 0) {
                    console.log('[EmotionSense] No messages detected. This might indicate WhatsApp Web structure changed.');
                }
            }, 3000);
        }
        
        console.log('[EmotionSense] 🚀 Extension fully initialized and ready!');
        
    } catch (error) {
        console.error('[EmotionSense] Initialization failed:', error);
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', enhancedInit);
} else {
    enhancedInit();
}
