// Debug script for WhatsApp message detection
// Paste this into WhatsApp Web console (F12) to test message extraction

console.log('🔍 EmotionSense Debug Script Started');

// Test all message selectors
const CONFIG_DEBUG = {
    messageSelectors: [
        'div[data-pre-plain-text] div[role="row"]',
        'div.message-in',
        'div[data-id*="false_"]',
        'div[aria-label*="Message"]',
        'div._21Ahp',
        'div._3_7SH',
        '[role="row"]',
        'div[data-testid="conversation-panel-messages"] > div > div'
    ],
    textSelectors: [
        'span.selectable-text[dir="ltr"]',
        'span.selectable-text',
        'span[data-testid="conversation-text"]',
        'span._11JPr',
        'span._3EFkT',
        'div._22Msk span',
        '.copyable-text span',
        'span[dir="auto"]',
        '[data-pre-plain-text] span'
    ],
    inputSelectors: [
        'div[contenteditable="true"][data-testid="conversation-compose-box-input"]',
        'div[contenteditable="true"][role="textbox"]',
        'footer div[contenteditable="true"]',
        'div[data-testid="compose-box"] div[contenteditable="true"]',
        'div._3uMse[contenteditable="true"]',
        'div._1awRl div[contenteditable="true"]'
    ]
};

function testMessageSelectors() {
    console.log('📝 Testing Message Selectors:');
    CONFIG_DEBUG.messageSelectors.forEach((selector, index) => {
        try {
            const elements = document.querySelectorAll(selector);
            const status = elements.length > 0 ? '✅' : '❌';
            console.log(`${status} ${index + 1}. ${selector} → Found ${elements.length} elements`);
            
            if (elements.length > 0 && index < 3) {
                // Show first few elements for successful selectors
                console.log('   Sample elements:', Array.from(elements).slice(0, 3));
            }
        } catch (error) {
            console.log(`❌ ${index + 1}. ${selector} → Error: ${error.message}`);
        }
    });
}

function testTextExtraction() {
    console.log('\n📖 Testing Text Extraction:');
    
    // First find message elements
    let messageElements = [];
    for (const selector of CONFIG_DEBUG.messageSelectors) {
        const found = document.querySelectorAll(selector);
        if (found.length > 0) {
            messageElements = Array.from(found);
            console.log(`Using messages from: ${selector} (${found.length} found)`);
            break;
        }
    }
    
    if (messageElements.length === 0) {
        console.log('❌ No message elements found');
        return;
    }
    
    // Test text extraction on last few messages
    const testMessages = messageElements.slice(-5); // Last 5 messages
    console.log(`🔍 Testing text extraction on ${testMessages.length} recent messages:`);
    
    testMessages.forEach((msgElement, index) => {
        console.log(`\n--- Message ${index + 1} ---`);
        
        CONFIG_DEBUG.textSelectors.forEach((textSelector, textIndex) => {
            try {
                const textElements = msgElement.querySelectorAll(textSelector);
                if (textElements.length > 0) {
                    const text = Array.from(textElements)
                        .map(el => el.textContent || el.innerText)
                        .filter(t => t && t.trim())
                        .join(' ')
                        .trim();
                    
                    if (text.length > 0) {
                        console.log(`✅ ${textSelector} → "${text.substring(0, 50)}${text.length > 50 ? '...' : ''}"`);
                    }
                }
            } catch (error) {
                // Ignore individual selector errors
            }
        });
        
        // Fallback extraction
        const fallbackText = msgElement.textContent || msgElement.innerText || '';
        const cleanText = fallbackText
            .replace(/\d{1,2}:\d{2}\s?(AM|PM)?/gi, '')
            .replace(/\n+/g, ' ')
            .replace(/\s+/g, ' ')
            .trim();
        
        if (cleanText) {
            console.log(`🔄 Fallback → "${cleanText.substring(0, 50)}${cleanText.length > 50 ? '...' : ''}"`);
        }
    });
}

function testInputDetection() {
    console.log('\n⌨️ Testing Input Detection:');
    CONFIG_DEBUG.inputSelectors.forEach((selector, index) => {
        try {
            const input = document.querySelector(selector);
            const status = input ? '✅' : '❌';
            console.log(`${status} ${index + 1}. ${selector}`);
            
            if (input) {
                console.log(`   Input element:`, input);
                console.log(`   Current content: "${input.textContent || input.value || '(empty)'}"`);
            }
        } catch (error) {
            console.log(`❌ ${index + 1}. ${selector} → Error: ${error.message}`);
        }
    });
}

function testMessageDetection() {
    console.log('\n🎯 Testing Complete Message Detection Flow:');
    
    // Simulate the extension's message detection
    let messages = [];
    let selectorUsed = null;
    
    for (const selector of CONFIG_DEBUG.messageSelectors) {
        try {
            const found = document.querySelectorAll(selector);
            if (found.length > 0) {
                messages = Array.from(found);
                selectorUsed = selector;
                break;
            }
        } catch (error) {
            console.warn(`Selector failed: ${selector}`, error);
        }
    }
    
    if (messages.length === 0) {
        console.log('❌ No messages found');
        return;
    }
    
    console.log(`✅ Found ${messages.length} messages using: ${selectorUsed}`);
    
    // Filter incoming messages
    const incomingMessages = messages.filter(msg => {
        const isOutgoing = msg.classList.contains('message-out') || 
                         msg.closest('.message-out') ||
                         msg.querySelector('[data-testid="tail-out"]') ||
                         msg.classList.contains('_3j7s9');
        return !isOutgoing;
    });
    
    console.log(`📨 Found ${incomingMessages.length} incoming messages`);
    
    if (incomingMessages.length > 0) {
        const lastMessage = incomingMessages[incomingMessages.length - 1];
        console.log('🔍 Last incoming message element:', lastMessage);
        
        // Extract text
        let text = '';
        for (const selector of CONFIG_DEBUG.textSelectors) {
            try {
                const textElements = lastMessage.querySelectorAll(selector);
                if (textElements.length > 0) {
                    text = Array.from(textElements)
                        .map(el => el.textContent || el.innerText)
                        .filter(t => t && t.trim())
                        .join(' ')
                        .trim();
                    
                    if (text.length > 0) {
                        console.log(`✅ Extracted text using ${selector}: "${text}"`);
                        break;
                    }
                }
            } catch (error) {
                // Continue to next selector
            }
        }
        
        if (!text) {
            const fallbackText = lastMessage.textContent || lastMessage.innerText || '';
            text = fallbackText
                .replace(/\d{1,2}:\d{2}\s?(AM|PM)?/gi, '')
                .replace(/\n+/g, ' ')
                .replace(/\s+/g, ' ')
                .trim();
            
            if (text) {
                console.log(`🔄 Extracted using fallback: "${text}"`);
            }
        }
        
        if (text && text.length >= 2) {
            console.log('🎉 SUCCESS: Ready to send for analysis!');
            console.log('📤 Would send to API:', { text, messageId: `test_${Date.now()}` });
        } else {
            console.log('❌ FAILED: No valid text extracted');
        }
    }
}

function checkExtensionStatus() {
    console.log('\n🔌 Checking Extension Status:');
    
    const launcher = document.querySelector('.emotionsense-launcher');
    if (launcher) {
        console.log('✅ Extension launcher found');
    } else {
        console.log('❌ Extension launcher not found');
    }
    
    const panel = document.querySelector('#emotionsense-panel');
    if (panel) {
        console.log('✅ Extension panel found');
    } else {
        console.log('❌ Extension panel not found');
    }
    
    // Check if chrome extension API is available
    if (typeof chrome !== 'undefined' && chrome.runtime) {
        console.log('✅ Chrome extension API available');
    } else {
        console.log('❌ Chrome extension API not available');
    }
}

// Run all tests
console.log('🚀 Running EmotionSense Debug Tests...\n');

checkExtensionStatus();
testMessageSelectors();
testTextExtraction();
testInputDetection();
testMessageDetection();

console.log('\n✨ Debug tests completed!');
console.log('\n💡 Next steps:');
console.log('1. If message detection works, test the API connection');
console.log('2. Open the API tester: http://localhost:5000 or use the test_page/api-test.html');
console.log('3. Check browser console for EmotionSense logs while using WhatsApp');