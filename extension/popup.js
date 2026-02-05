// Popup Script for EmotionSense Extension

// Load settings on popup open
document.addEventListener('DOMContentLoaded', loadSettings);

// Save button click
document.getElementById('saveBtn').addEventListener('click', saveSettings);

// Load settings from storage
async function loadSettings() {
    try {
        const settings = await chrome.storage.sync.get({
            enabled: true,
            whatsappEnabled: true,
            instagramEnabled: true,
            tone: 'caring',
            apiUrl: 'http://localhost:5000'
        });

        document.getElementById('enabled').checked = settings.enabled;
        document.getElementById('whatsappEnabled').checked = settings.whatsappEnabled;
        document.getElementById('instagramEnabled').checked = settings.instagramEnabled;
        document.getElementById('tone').value = settings.tone;
        document.getElementById('apiUrl').value = settings.apiUrl;

    } catch (error) {
        console.error('Error loading settings:', error);
        showStatus('Error loading settings', 'error');
    }
}

// Save settings to storage
async function saveSettings() {
    const settings = {
        enabled: document.getElementById('enabled').checked,
        whatsappEnabled: document.getElementById('whatsappEnabled').checked,
        instagramEnabled: document.getElementById('instagramEnabled').checked,
        tone: document.getElementById('tone').value,
        apiUrl: document.getElementById('apiUrl').value.trim()
    };

    try {
        await chrome.storage.sync.set(settings);
        showStatus('Settings saved successfully!', 'success');

        // Auto-hide success message after 2 seconds
        setTimeout(() => {
            hideStatus();
        }, 2000);

    } catch (error) {
        console.error('Error saving settings:', error);
        showStatus('Error saving settings', 'error');
    }
}

// Show status message
function showStatus(message, type) {
    const statusEl = document.getElementById('status');
    statusEl.textContent = message;
    statusEl.className = `status ${type}`;
}

// Hide status message
function hideStatus() {
    const statusEl = document.getElementById('status');
    statusEl.className = 'status';
}
