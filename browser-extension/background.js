// Background service worker for FinACCAI extension

// Try multiple localhost variations for better compatibility
const API_URLS = [
  'http://localhost:5000/api/analyze',
  'http://127.0.0.1:5000/api/analyze',
  'http://[::1]:5000/api/analyze'
];

// Test health endpoint
async function testAPIHealth() {
  for (const url of API_URLS) {
    const baseUrl = url.replace('/api/analyze', '/api/health');
    try {
      const response = await fetch(baseUrl, { method: 'GET', timeout: 2000 });
      if (response.ok) {
        return url;
      }
    } catch (e) {
      // Continue to next URL
    }
  }
  return null;
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'analyzeWithBackend') {
    // Try to find working API URL
    testAPIHealth().then(workingUrl => {
      if (!workingUrl) {
        console.warn('API not available, falling back to client-side analysis');
        sendResponse({ success: false, error: 'API not available' });
        return;
      }
      
      // Send HTML content to backend API for analysis
      fetch(workingUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          html: request.html,
          url: request.url,
          title: request.title,
          level: request.level || 'AAA',
          screenshot: request.screenshot || null
        }),
        timeout: 30000
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('✓ Backend analysis successful');
        sendResponse({ success: true, data: data });
      })
      .catch(error => {
        console.error('Backend analysis error:', error);
        sendResponse({ success: false, error: error.toString() });
      });
    });
    
    return true; // Keep the message channel open for async response
  }
});
