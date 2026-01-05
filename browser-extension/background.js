// Background service worker for FinACCAI extension
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'analyzeWithBackend') {
    // Send HTML content to backend API for analysis
    fetch('http://localhost:5000/api/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        html: request.html,
        url: request.url,
        title: request.title
      })
    })
    .then(response => response.json())
    .then(data => {
      sendResponse({ success: true, data: data });
    })
    .catch(error => {
      sendResponse({ success: false, error: error.toString() });
    });
    
    return true; // Keep the message channel open for async response
  }
});
