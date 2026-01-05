// Popup script for FinACCAI extension
let currentReport = null;

document.addEventListener('DOMContentLoaded', async function() {
  const analyzeBtn = document.getElementById('analyzeBtn');
  const statusDiv = document.getElementById('status');
  const resultsDiv = document.getElementById('results');
  const quickChecksDiv = document.getElementById('quickChecks');
  const aiStatusDiv = document.getElementById('aiStatus');
  const viewFullReportBtn = document.getElementById('viewFullReport');
  const downloadReportBtn = document.getElementById('downloadReport');
  
  // Check current tab on load
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab.url.startsWith('chrome://') || tab.url.startsWith('edge://') || 
        tab.url.startsWith('chrome-extension://') || tab.url.startsWith('about:')) {
      statusDiv.innerHTML = '<p>⚠️ Cannot analyze browser internal pages. Please navigate to a regular webpage.</p>';
      statusDiv.className = 'status';
      analyzeBtn.disabled = true;
    }
  } catch (e) {
    console.log('Error checking tab:', e);
  }
  
  analyzeBtn.addEventListener('click', analyzePage);
  viewFullReportBtn.addEventListener('click', viewFullReport);
  downloadReportBtn.addEventListener('click', downloadReport);
  
  async function analyzePage() {
    analyzeBtn.disabled = true;
    statusDiv.innerHTML = '<div class="spinner"></div><p>Analyzing current page...</p>';
    statusDiv.className = 'status loading';
    resultsDiv.classList.add('hidden');
    
    try {
      // Get the current tab
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      // Check if the page is a restricted page
      if (tab.url.startsWith('chrome://') || tab.url.startsWith('edge://') || 
          tab.url.startsWith('chrome-extension://') || tab.url.startsWith('about:')) {
        showError('Cannot analyze browser internal pages. Please navigate to a regular webpage.');
        analyzeBtn.disabled = false;
        return;
      }
      
      // Try to inject content script if it's not already loaded
      try {
        await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          files: ['content.js']
        });
      } catch (e) {
        // Content script might already be injected, continue
        console.log('Content script injection:', e.message);
      }
      
      // Wait a moment for content script to load
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Send message to content script to analyze the page
      chrome.tabs.sendMessage(tab.id, { action: 'analyzePage' }, async (response) => {
        if (chrome.runtime.lastError) {
          showError('Could not connect to page. Please refresh the page and try again. Error: ' + chrome.runtime.lastError.message);
          analyzeBtn.disabled = false;
          return;
        }
        
        if (!response.success) {
          showError('Error analyzing page: ' + response.error);
          analyzeBtn.disabled = false;
          return;
        }
        
        // Display client-side check results
        displayQuickChecks(response.clientChecks);
        
        // Send to backend for AI analysis
        statusDiv.innerHTML = '<div class="spinner"></div><p>Running AI analysis...</p>';
        
        chrome.runtime.sendMessage({
          action: 'analyzeWithBackend',
          html: response.html,
          url: response.url,
          title: response.title
        }, (backendResponse) => {
          analyzeBtn.disabled = false;
          
          if (backendResponse && backendResponse.success) {
            currentReport = backendResponse.data;
            displayAIStatus(backendResponse.data);
            statusDiv.innerHTML = '<p>✓ Full scan complete!</p>';
            statusDiv.className = 'status success';
            resultsDiv.classList.remove('hidden');
            viewFullReportBtn.classList.remove('hidden');
            downloadReportBtn.classList.remove('hidden');
          } else {
            // Show client checks even if backend fails
            aiStatusDiv.innerHTML = `
              <p style="color: #856404;">⚠ Backend API not available</p>
              <p style="font-size: 12px;">Make sure the FinACCAI server is running on localhost:5000</p>
              <p style="font-size: 12px;">You can still see basic client-side checks above.</p>
            `;
            statusDiv.innerHTML = '<p>⚠ Partial analysis (client-side only)</p>';
            statusDiv.className = 'status';
            resultsDiv.classList.remove('hidden');
          }
        });
      });
    } catch (error) {
      showError('Error: ' + error.toString());
      analyzeBtn.disabled = false;
    }
  }
  
  function displayQuickChecks(checks) {
    const totalIssues = Object.values(checks).reduce((sum, arr) => sum + arr.length, 0);
    
    let html = `<div class="issue-count">
      <span class="issue-label">Total Issues Found:</span>
      <span class="issue-number ${totalIssues === 0 ? 'success' : ''}">${totalIssues}</span>
    </div>`;
    
    const categories = [
      { key: 'images', label: 'Missing Alt Text', icon: '🖼️' },
      { key: 'inputs', label: 'Unlabeled Inputs', icon: '📝' },
      { key: 'headings', label: 'Heading Hierarchy', icon: '📑' },
      { key: 'links', label: 'Link Issues', icon: '🔗' },
      { key: 'aria', label: 'ARIA Issues', icon: '♿' }
    ];
    
    categories.forEach(cat => {
      const count = checks[cat.key].length;
      const categoryId = `category-${cat.key}`;
      
      html += `
        <div class="issue-category">
          <div class="issue-count clickable" onclick="toggleDetails('${categoryId}')">
            <span class="issue-label">
              ${cat.icon} ${cat.label}:
              <span class="toggle-icon" id="toggle-${categoryId}">▶</span>
            </span>
            <span class="issue-number ${count === 0 ? 'success' : ''}">${count}</span>
          </div>
          <div class="issue-details" id="${categoryId}" style="display: none;">
            ${formatIssueDetails(cat.key, checks[cat.key])}
          </div>
        </div>`;
    });
    
    quickChecksDiv.innerHTML = html;
    
    // Add global toggle function
    window.toggleDetails = function(id) {
      const details = document.getElementById(id);
      const toggle = document.getElementById('toggle-' + id);
      if (details.style.display === 'none') {
        details.style.display = 'block';
        toggle.textContent = '▼';
      } else {
        details.style.display = 'none';
        toggle.textContent = '▶';
      }
    };
  }
  
  function formatIssueDetails(category, issues) {
    if (issues.length === 0) {
      return '<p class="no-issues">✓ No issues found</p>';
    }
    
    let html = '<ul class="issue-list">';
    
    issues.forEach((issue, index) => {
      switch(category) {
        case 'images':
          html += `<li class="issue-item">
            <strong>Image ${index + 1}:</strong><br>
            <span class="issue-detail">Source: ${issue.src || 'N/A'}</span><br>
            <code class="issue-code">${escapeHtml(issue.snippet)}</code>
          </li>`;
          break;
          
        case 'inputs':
          html += `<li class="issue-item">
            <strong>Input ${index + 1}:</strong> ${issue.type || 'text'}<br>
            ${issue.id ? `<span class="issue-detail">ID: ${issue.id}</span><br>` : ''}
            ${issue.name ? `<span class="issue-detail">Name: ${issue.name}</span><br>` : ''}
            <code class="issue-code">${escapeHtml(issue.snippet)}</code>
          </li>`;
          break;
          
        case 'headings':
          html += `<li class="issue-item">
            <strong>Heading ${index + 1}:</strong><br>
            <span class="issue-detail">${issue.message}</span><br>
            <span class="issue-detail">Text: "${issue.text}"</span>
          </li>`;
          break;
          
        case 'links':
          html += `<li class="issue-item">
            <strong>Link ${index + 1}:</strong><br>
            <span class="issue-detail">${issue.message}</span><br>
            ${issue.text ? `<span class="issue-detail">Text: "${issue.text}"</span><br>` : ''}
            ${issue.href ? `<span class="issue-detail">URL: ${issue.href}</span><br>` : ''}
            <code class="issue-code">${escapeHtml(issue.snippet)}</code>
          </li>`;
          break;
          
        case 'aria':
          html += `<li class="issue-item">
            <strong>ARIA ${index + 1}:</strong> role="${issue.role}"<br>
            <span class="issue-detail">${issue.message}</span><br>
            <code class="issue-code">${escapeHtml(issue.snippet)}</code>
          </li>`;
          break;
      }
    });
    
    html += '</ul>';
    return html;
  }
  
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
  
  function displayAIStatus(data) {
    let html = '<p>✓ ML/NLP Analysis: Complete</p>';
    html += '<p>✓ Vision Analysis: Complete</p>';
    html += '<p>✓ XAI Explanations: Generated</p>';
    aiStatusDiv.innerHTML = html;
  }
  
  function showError(message) {
    statusDiv.innerHTML = `<p>✗ ${message}</p>`;
    statusDiv.className = 'status error';
  }
  
  function viewFullReport() {
    if (currentReport && currentReport.reportPath) {
      // Open the generated report in a new tab
      chrome.tabs.create({ url: `http://localhost:5000/reports/${currentReport.reportPath}` });
    } else {
      alert('Report not available. Make sure the backend server is running.');
    }
  }
  
  function downloadReport() {
    if (currentReport && currentReport.reportPath) {
      // Download the report
      chrome.downloads.download({
        url: `http://localhost:5000/reports/${currentReport.reportPath}`,
        filename: `accessibility_report_${Date.now()}.html`
      });
    } else {
      alert('Report not available. Make sure the backend server is running.');
    }
  }
});
