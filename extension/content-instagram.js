// Content Script for Instagram DMs
// Detects incoming messages and displays suggestion panel

console.log('[EmotionSense] Instagram content script loaded');

// Configuration
const CONFIG = {
    messageContainerSelector: 'div[role="grid"]',
    messageRowSelector: 'div[role="row"]',
    textSelector: 'div[dir="auto"]',
    inputSelector: 'div[contenteditable="true"][role="textbox"]',
    checkInterval: 1000
};

// State
let lastProcessedMessage = null;
let suggestionPanel = null;
let observer = null;

// Initialize
function init() {
    console.log('[EmotionSense] Initializing Instagram integration');

    // Wait for chat to load
    waitForChat();
}

// Wait for chat interface to load
function waitForChat() {
    const checkChat = setInterval(() => {
        const chatContainer = document.querySelector(CONFIG.messageContainerSelector);
        if (chatContainer) {
            clearInterval(checkChat);
            console.log('[EmotionSense] Chat detected, starting monitoring');

            // Create suggestion panel
            createSuggestionPanel();

            // Start monitoring
            startMessageMonitoring();
        }
    }, 1000);
}

// Monitor for new incoming messages using MutationObserver
function startMessageMonitoring() {
    const chatContainer = document.querySelector(CONFIG.messageContainerSelector);
    if (!chatContainer) return;

    // Use MutationObserver for better performance
    observer = new MutationObserver((mutations) => {
        for (const mutation of mutations) {
            if (mutation.addedNodes.length > 0) {
                checkForNewMessages();
            }
        }
    });

    observer.observe(chatContainer, {
        childList: true,
        subtree: true
    });

    // Also check periodically as fallback
    setInterval(checkForNewMessages, CONFIG.checkInterval);
}

// Check for new messages
function checkForNewMessages() {
    const messages = document.querySelectorAll(CONFIG.messageRowSelector);
    if (messages.length === 0) return;

    // Get the last message
    const lastMessage = messages[messages.length - 1];

    // Check if it's an incoming message (left-aligned)
    const isIncoming = isIncomingMessage(lastMessage);
    if (!isIncoming) return;

    // Generate unique ID for the message
    const messageId = generateMessageId(lastMessage);

    // Skip if already processed
    if (messageId === lastProcessedMessage) return;

    // Extract message text
    const textElement = lastMessage.querySelector(CONFIG.textSelector);
    if (!textElement) return;

    const messageText = textElement.innerText.trim();
    if (!messageText) return;

    // Process the message
    lastProcessedMessage = messageId;
    processMessage(messageText, messageId);
}

// Check if message is incoming (from partner)
function isIncomingMessage(messageElement) {
    // Instagram shows incoming messages on the left
    // Check for specific classes or positioning
    const rect = messageElement.getBoundingClientRect();
    const containerRect = messageElement.parentElement.getBoundingClientRect();

    // If message is on the left side, it's incoming
    return rect.left < containerRect.left + (containerRect.width / 2);
}

// Generate unique message ID
function generateMessageId(messageElement) {
    const text = messageElement.innerText;
    const timestamp = Date.now();
    return `${text.substring(0, 20)}_${timestamp}`;
}

// Process incoming message
async function processMessage(text, messageId) {
    console.log('[EmotionSense] Processing message:', text);

    // Show loading state
    showSuggestionPanel('loading');

    // Send to background script for analysis
    chrome.runtime.sendMessage({
        action: 'analyzeMessage',
        data: { text, messageId }
    }, (response) => {
        if (response && response.success) {
            displaySuggestions(response.data);
        } else {
            console.error('[EmotionSense] Analysis failed:', response?.error);
            hideSuggestionPanel();
        }
    });
}

// Create suggestion panel UI
function createSuggestionPanel() {
    suggestionPanel = document.createElement('div');
    suggestionPanel.id = 'emotionsense-panel';
    suggestionPanel.className = 'emotionsense-hidden emotionsense-instagram';
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
        ? 'emotionsense-visible emotionsense-instagram emotionsense-loading-state'
        : 'emotionsense-visible emotionsense-instagram';
}

// Hide suggestion panel
function hideSuggestionPanel() {
    if (!suggestionPanel) return;
    suggestionPanel.className = 'emotionsense-hidden emotionsense-instagram';
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
        showToast('Copied to clipboard!');
    });
}

// Insert text into chat input
function insertIntoChat(text) {
    const inputBox = document.querySelector(CONFIG.inputSelector);
    if (!inputBox) {
        console.error('[EmotionSense] Chat input not found');
        return;
    }

    // Set the text
    inputBox.textContent = text;

    // Trigger input event
    const event = new InputEvent('input', {
        bubbles: true,
        cancelable: true
    });
    inputBox.dispatchEvent(event);

    // Focus the input
    inputBox.focus();

    // Hide panel
    hideSuggestionPanel();

    showToast('Inserted into chat!');
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

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
