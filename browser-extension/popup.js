// Popup script for FinACCAI extension
let currentReport = null;

document.addEventListener('DOMContentLoaded', function() {
  const analyzeBtn = document.getElementById('analyzeBtn');
  const statusDiv = document.getElementById('status');
  const resultsDiv = document.getElementById('results');
  const quickChecksDiv = document.getElementById('quickChecks');
  const aiStatusDiv = document.getElementById('aiStatus');
  const viewFullReportBtn = document.getElementById('viewFullReport');
  const downloadReportBtn = document.getElementById('downloadReport');
  
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
      
      // Send message to content script to analyze the page
      chrome.tabs.sendMessage(tab.id, { action: 'analyzePage' }, async (response) => {
        if (chrome.runtime.lastError) {
          showError('Could not connect to page. Try refreshing the page.');
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
            statusDiv.innerHTML = '<p>✓ Analysis complete!</p>';
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
      { key: 'images', label: 'Missing Alt Text' },
      { key: 'inputs', label: 'Unlabeled Inputs' },
      { key: 'headings', label: 'Heading Hierarchy' },
      { key: 'links', label: 'Link Issues' },
      { key: 'aria', label: 'ARIA Issues' }
    ];
    
    categories.forEach(cat => {
      const count = checks[cat.key].length;
      html += `<div class="issue-count">
        <span class="issue-label">${cat.label}:</span>
        <span class="issue-number ${count === 0 ? 'success' : ''}">${count}</span>
      </div>`;
    });
    
    quickChecksDiv.innerHTML = html;
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
