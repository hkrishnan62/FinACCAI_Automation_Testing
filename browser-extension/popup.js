// Popup script for FinACCAI extension
let currentReport = null;
let currentPageData = null;  // Store current page analysis data
let currentScreenshot = null;  // Store current page screenshot

// Test API availability with multiple URLs
async function testAPIConnection() {
  const apiUrls = [
    'http://localhost:5000/api/health',
    'http://127.0.0.1:5000/api/health'
  ];
  
  for (const url of apiUrls) {
    try {
      const response = await fetch(url, { method: 'GET' });
      if (response.ok) {
        return url.replace('/api/health', '/api/analyze');
      }
    } catch (e) {
      // Try next URL
    }
  }
  return null;
}

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
  
  // Update level description when dropdown changes
  const levelSelect = document.getElementById('levelSelect');
  const levelInfo = document.querySelector('.level-info');
  if (levelSelect && levelInfo) {
    levelSelect.addEventListener('change', function() {
      const descriptions = {
        'A': 'Minimum accessibility - Basic requirements for all web content',
        'AA': 'Standard compliance - Meets most accessibility needs (4.5:1 contrast)',
        'AAA': 'Enhanced accessibility - Highest level with strict requirements (7:1 contrast)'
      };
      levelInfo.textContent = descriptions[this.value] || descriptions['AAA'];
    });
  }
  
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
        
        // Store page data for report generation
        currentPageData = response;
        
        // Display client-side check results
        displayQuickChecks(response.clientChecks);
        
        // Highlight issues on the page
        statusDiv.textContent = '🎯 Highlighting issues on page...';
        try {
          await chrome.tabs.sendMessage(tab.id, {
            action: 'highlightElements',
            issues: response.clientChecks
          });
          // Wait for highlights to render
          await new Promise(resolve => setTimeout(resolve, 500));
        } catch (e) {
          console.warn('Could not highlight elements:', e);
        }
        
        // Capture full page screenshot WITH HIGHLIGHTS
        statusDiv.textContent = '📸 Capturing screenshot with highlighted issues...';
        let screenshotData = null;
        try {
          const screenshotBase64 = await captureFullPageScreenshot(tab.id);
          if (screenshotBase64) {
            // Store screenshot for later use
            currentScreenshot = screenshotBase64;
            // Remove data:image/png;base64, prefix if present
            screenshotData = screenshotBase64.replace(/^data:image\/png;base64,/, '');
            displayScreenshot(screenshotBase64);
          }
        } catch (e) {
          console.warn('Screenshot capture failed:', e);
        }
        
        statusDiv.innerHTML = '<div class="spinner"></div><p>Running AI analysis...</p>';
        
        // Try direct API call first (faster, works from extension context)
        const apiUrl = await testAPIConnection();
        // Get selected WCAG level from dropdown
        const selectedLevel = document.getElementById('levelSelect') ? document.getElementById('levelSelect').value : 'AAA';
        
        if (apiUrl) {
          try {
            const backendResponse = await fetch(apiUrl, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                html: response.html,
                url: response.url,
                title: response.title,
                level: selectedLevel,
                screenshot: screenshotData
              })
            });
            
            if (backendResponse.ok) {
              const data = await backendResponse.json();
              analyzeBtn.disabled = false;
              currentReport = data;
              displayAIStatus(data);
              statusDiv.innerHTML = '<p>✓ Full scan complete!</p>';
              statusDiv.className = 'status success';
              resultsDiv.classList.remove('hidden');
              viewFullReportBtn.classList.remove('hidden');
              downloadReportBtn.classList.remove('hidden');
              return;
            }
          } catch (e) {
            console.warn('Direct API call failed, trying service worker:', e);
          }
        }
        
        // Fallback: Use service worker
        chrome.runtime.sendMessage({
          action: 'analyzeWithBackend',
          html: response.html,
          url: response.url,
          title: response.title,
          level: selectedLevel,
          screenshot: screenshotData
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
              <p style="font-size: 12px;">Client-side analysis completed successfully.</p>
              <p style="font-size: 12px;">You can download a report of the findings below.</p>
            `;
            statusDiv.innerHTML = '<p>✓ Client-side scan complete</p>';
            statusDiv.className = 'status success';
            resultsDiv.classList.remove('hidden');
            downloadReportBtn.classList.remove('hidden');
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
    let html = '';
    
    if (data.ai_ml_enabled) {
      html += '<p style="color: #28a745;">✓ Full AI/ML Analysis Complete</p>';
      html += '<ul style="font-size: 12px; margin: 10px 0; padding-left: 20px;">';
      html += '<li>🤖 Machine Learning predictions</li>';
      html += '<li>📝 Natural Language Processing</li>';
      html += '<li>🖼️ Vision analysis</li>';
      html += '<li>💡 Explainable AI insights</li>';
      html += '</ul>';
      
      if (data.ai_ml_results) {
        const status = data.ai_ml_results.status;
        if (status === 'AI/ML analysis completed') {
          html += '<p style="font-size: 11px; color: #666; margin-top: 10px;">Advanced analysis techniques applied to detect complex accessibility issues.</p>';
        } else {
          html += `<p style="font-size: 11px; color: #856404; margin-top: 10px;">${status}</p>`;
        }
      }
    } else {
      html += '<p style="color: #856404;">⚠ AI/ML Features Not Enabled</p>';
      html += '<p style="font-size: 11px;">AI/ML libraries are not installed on the server.</p>';
      html += '<p style="font-size: 11px;">Current analysis uses rule-based checks only.</p>';
      html += '<details style="font-size: 11px; margin-top: 10px;"><summary style="cursor: pointer; color: #667eea;">How to enable AI/ML</summary>';
      html += '<code style="display: block; background: #f4f4f4; padding: 5px; margin-top: 5px;">pip install transformers torch scikit-learn pillow</code>';
      html += '</details>';
    }
    
    aiStatusDiv.innerHTML = html;
  }
  
  function showError(message) {
    statusDiv.innerHTML = `<p>✗ ${message}</p>`;
    statusDiv.className = 'status error';
  }
  
  // Capture full page screenshot
  async function captureFullPageScreenshot(tabId) {
    try {
      // First, scroll to top of page to ensure consistent capture
      await chrome.tabs.sendMessage(tabId, {
        action: 'executeScript',
        script: 'window.scrollTo(0, 0);'
      }).catch(() => {});
      
      // Wait for scroll to complete and page to render
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Capture the visible viewport (which now shows the top of the page with highlights)
      const screenshot = await chrome.tabs.captureVisibleTab(null, {
        format: 'png',
        quality: 100
      });
      
      return screenshot;
    } catch (error) {
      console.error('Full page screenshot error:', error);
      // Try a simple capture without scrolling
      try {
        return await chrome.tabs.captureVisibleTab(null, {
          format: 'png',
          quality: 90
        });
      } catch (fallbackError) {
        console.error('Fallback screenshot also failed:', fallbackError);
        return null;
      }
    }
  }
  
  // Capture individual issue element screenshot
  async function captureIssueScreenshot(tabId, issueData) {
    try {
      // Scroll to element
      await chrome.tabs.sendMessage(tabId, {
        action: 'scrollToElement',
        selector: issueData.selector
      });
      
      // Highlight the issue
      await chrome.tabs.sendMessage(tabId, {
        action: 'highlightElements',
        issues: [issueData]
      });
      
      // Wait for render
      await new Promise(resolve => setTimeout(resolve, 400));
      
      // Capture screenshot
      const screenshot = await chrome.tabs.captureVisibleTab(null, {
        format: 'png',
        quality: 95
      });
      
      // Remove highlights
      await chrome.tabs.sendMessage(tabId, {
        action: 'removeHighlights'
      }).catch(() => {});
      
      return screenshot;
    } catch (error) {
      console.error('Issue screenshot error:', error);
      return null;
    }
  }
  
  // Capture screenshots for multiple issues
  async function captureIssueScreenshots(tabId, issues) {
    const screenshots = {};
    
    for (let i = 0; i < Math.min(issues.length, 5); i++) {
      const issue = issues[i];
      if (issue.element && issue.element.outerHTML) {
        const screenshot = await captureIssueScreenshot(tabId, issue);
        if (screenshot) {
          screenshots[`issue_${i}`] = screenshot;
        }
      }
    }
    
    return screenshots;
  }
  
  // Display screenshot in popup
  function displayScreenshot(screenshotUrl) {
    const existingScreenshot = document.querySelector('.screenshot-section');
    if (existingScreenshot) {
      existingScreenshot.remove();
    }
    
    const screenshotSection = document.createElement('div');
    screenshotSection.className = 'screenshot-section';
    screenshotSection.innerHTML = `
      <h3>📸 Error Screenshot</h3>
      <div class="screenshot-container">
        <img src="${screenshotUrl}" alt="Screenshot with highlighted errors" 
             style="width: 100%; border-radius: 4px; border: 1px solid #ddd; cursor: pointer;"
             onclick="window.open('${screenshotUrl}', '_blank')">
        <p style="font-size: 11px; color: #666; margin-top: 5px; text-align: center;">
          Failing elements are highlighted in red with numbered badges. Click to enlarge.
        </p>
      </div>
    `;
    
    const quickChecks = document.getElementById('quickChecks');
    if (quickChecks && quickChecks.firstChild) {
      quickChecks.insertBefore(screenshotSection, quickChecks.firstChild);
    }
  }
  
  function viewFullReport() {
    if (currentReport && currentReport.reportPath) {
      // Open the generated report in a new tab
      chrome.tabs.create({ url: `http://localhost:5000/reports/${currentReport.reportPath}` });
    } else {
      alert('Report not available. Make sure the backend server is running.');
    }
  }
  
  async function downloadReport() {
    // Use stored page data for report generation
    if (currentPageData) {
      // Use already captured screenshot if available
      let fullPageScreenshot = currentScreenshot;
      
      // If no screenshot stored, try to capture one now
      if (!fullPageScreenshot) {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        statusDiv.textContent = '📸 Capturing full page screenshot...';
        fullPageScreenshot = await captureFullPageScreenshot(tab.id);
      }
      
      const reportHtml = await generateClientReport(currentPageData.url, currentPageData.title, currentPageData.clientChecks, fullPageScreenshot);
      downloadHtmlFile(reportHtml, `accessibility_report_${Date.now()}.html`);
      return;
    }
    
    // Fallback: try to get backend report if available
    if (currentReport && currentReport.reportPath) {
      const reportUrl = `http://localhost:5000/reports/${currentReport.reportPath}`;
      chrome.tabs.create({ url: reportUrl });
    } else {
      alert('No report data available. Please analyze the page first.');
    }
  }
  
  async function generateClientReport(url, title, checks, screenshotUrl = null) {
    const timestamp = new Date().toLocaleString();
    const totalIssues = Object.values(checks).reduce((sum, arr) => sum + arr.length, 0);
    
    let html = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Accessibility Report - ${escapeHtml(title)}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .header h1 { margin: 0 0 10px 0; }
        .summary {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .summary-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        .summary-item:last-child { border-bottom: none; }
        .count {
            font-weight: bold;
            font-size: 24px;
            color: #dc3545;
        }
        .count.success { color: #28a745; }
        .category {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .category h2 {
            margin: 0 0 15px 0;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
            color: #333;
        }
        .issue {
            background: #f8f9fa;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #dc3545;
            border-radius: 4px;
        }
        .issue-title {
            font-weight: bold;
            color: #333;
            margin-bottom: 8px;
        }
        .issue-detail {
            color: #666;
            font-size: 14px;
            margin: 5px 0;
        }
        .code {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 10px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            overflow-x: auto;
            margin-top: 10px;
            white-space: pre-wrap;
            word-break: break-all;
        }
        .no-issues {
            color: #28a745;
            font-style: italic;
            padding: 20px;
            text-align: center;
        }
        .element-id {
            background: #e3f2fd;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
            font-size: 12px;
        }
        .issue-screenshot {
            margin-top: 15px;
            padding: 12px;
            background: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 6px;
            text-align: center;
        }
        .issue-screenshot img {
            max-width: 100%;
            max-height: 400px;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }
        .issue-screenshot-label {
            font-size: 12px;
            color: #666;
            margin-top: 8px;
            font-style: italic;
        }
        .full-page-screenshot {
            margin: 20px 0;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .full-page-screenshot img {
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 FinACCAI Accessibility Report</h1>
        <p><strong>Page:</strong> ${escapeHtml(title)}</p>
        <p><strong>URL:</strong> ${escapeHtml(url)}</p>
        <p><strong>Generated:</strong> ${timestamp}</p>
        <p><em>Client-side analysis</em></p>
    </div>
        ${screenshotUrl ? `
    <div class="full-page-screenshot">
        <h2>📸 Full Page Screenshot</h2>
        <p style="color: #666; margin-bottom: 15px;">Complete view of the analyzed page. Errors are highlighted in red with numbered badges.</p>
        <img src="${screenshotUrl}" alt="Full page screenshot with highlighted errors">
        <p style="color: #999; font-size: 12px; margin-top: 10px;">Reference numbers match the issue list below</p>
    </div>
    ` : ''}
        <div class="summary">
        <h2>Summary</h2>
        <div class="summary-item">
            <span>Total Issues Found:</span>
            <span class="count ${totalIssues === 0 ? 'success' : ''}">${totalIssues}</span>
        </div>
        <div class="summary-item">
            <span>🖼️ Missing Alt Text:</span>
            <span class="count ${checks.images.length === 0 ? 'success' : ''}">${checks.images.length}</span>
        </div>
        <div class="summary-item">
            <span>📝 Unlabeled Inputs:</span>
            <span class="count ${checks.inputs.length === 0 ? 'success' : ''}">${checks.inputs.length}</span>
        </div>
        <div class="summary-item">
            <span>📑 Heading Hierarchy:</span>
            <span class="count ${checks.headings.length === 0 ? 'success' : ''}">${checks.headings.length}</span>
        </div>
        <div class="summary-item">
            <span>🔗 Link Issues:</span>
            <span class="count ${checks.links.length === 0 ? 'success' : ''}">${checks.links.length}</span>
        </div>
        <div class="summary-item">
            <span>♿ ARIA Issues:</span>
            <span class="count ${checks.aria.length === 0 ? 'success' : ''}">${checks.aria.length}</span>
        </div>
    </div>
`;
    
    // Images section
    html += generateReportSection('🖼️ Missing Alt Text', checks.images, (issue, i) => `
        <div class="issue">
            <div class="issue-title">Issue #${i}: Image without alt text</div>
            <div class="issue-detail"><strong>Element:</strong> &lt;img&gt;</div>
            <div class="issue-detail"><strong>Source:</strong> ${escapeHtml(issue.src || 'N/A')}</div>
            <div class="code">${escapeHtml(issue.snippet)}</div>
        </div>
    `, '✓ No issues found - all images have alt text');
    
    // Inputs section
    html += generateReportSection('📝 Unlabeled Input Fields', checks.inputs, (issue, i) => `
        <div class="issue">
            <div class="issue-title">Issue #${i}: Input without proper label</div>
            <div class="issue-detail"><strong>Element:</strong> &lt;input type="${issue.type || 'text'}"&gt;</div>
            ${issue.id ? `<div class="issue-detail"><strong>ID:</strong> <span class="element-id">${escapeHtml(issue.id)}</span></div>` : ''}
            ${issue.name ? `<div class="issue-detail"><strong>Name:</strong> <span class="element-id">${escapeHtml(issue.name)}</span></div>` : ''}
            <div class="code">${escapeHtml(issue.snippet)}</div>
        </div>
    `, '✓ No issues found - all inputs are properly labeled');
    
    // Headings section
    html += generateReportSection('📑 Heading Hierarchy Issues', checks.headings, (issue, i) => `
        <div class="issue">
            <div class="issue-title">Issue #${i}: Heading hierarchy problem</div>
            <div class="issue-detail"><strong>Problem:</strong> ${escapeHtml(issue.message)}</div>
            <div class="issue-detail"><strong>Heading text:</strong> "${escapeHtml(issue.text)}"</div>
        </div>
    `, '✓ No issues found - heading hierarchy is correct');
    
    // Links section
    html += generateReportSection('🔗 Link Accessibility Issues', checks.links, (issue, i) => `
        <div class="issue">
            <div class="issue-title">Issue #${i}: Link accessibility problem</div>
            <div class="issue-detail"><strong>Problem:</strong> ${escapeHtml(issue.message)}</div>
            ${issue.text ? `<div class="issue-detail"><strong>Link text:</strong> "${escapeHtml(issue.text)}"</div>` : ''}
            ${issue.href ? `<div class="issue-detail"><strong>URL:</strong> ${escapeHtml(issue.href)}</div>` : ''}
            <div class="code">${escapeHtml(issue.snippet)}</div>
        </div>
    `, '✓ No issues found - all links are accessible');
    
    // ARIA section
    html += generateReportSection('♿ ARIA Accessibility Issues', checks.aria, (issue, i) => `
        <div class="issue">
            <div class="issue-title">Issue #${i}: ARIA attribute problem</div>
            <div class="issue-detail"><strong>Element role:</strong> <span class="element-id">${escapeHtml(issue.role)}</span></div>
            <div class="issue-detail"><strong>Problem:</strong> ${escapeHtml(issue.message)}</div>
            <div class="code">${escapeHtml(issue.snippet)}</div>
        </div>
    `, '✓ No issues found - ARIA attributes are correct');
    
    html += '</body></html>';
    return html;
  }
  
  function generateReportSection(title, issues, issueFormatter, noIssuesMessage) {
    let html = `<div class="category"><h2>${title} (${issues.length} issues)</h2>`;
    
    if (issues.length > 0) {
      issues.forEach((issue, index) => {
        html += issueFormatter(issue, index + 1);
      });
    } else {
      html += `<div class="no-issues">${noIssuesMessage}</div>`;
    }
    
    html += '</div>';
    return html;
  }
  
  function downloadHtmlFile(content, filename) {
    const blob = new Blob([content], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    chrome.downloads.download({
      url: url,
      filename: filename,
      saveAs: true
    });
  }
});
