// Content script for FinACCAI extension
// This runs on every page and can analyze the DOM

// Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'analyzePage') {
    try {
      // Get the full HTML of the page
      const htmlContent = document.documentElement.outerHTML;
      const pageTitle = document.title;
      const pageUrl = window.location.href;
      
      // Perform client-side checks
      const clientChecks = performClientSideChecks();
      
      sendResponse({
        success: true,
        html: htmlContent,
        title: pageTitle,
        url: pageUrl,
        clientChecks: clientChecks
      });
    } catch (error) {
      sendResponse({
        success: false,
        error: error.toString()
      });
    }
    return true;
  }
});

function performClientSideChecks() {
  const issues = {
    images: [],
    inputs: [],
    contrast: [],
    headings: [],
    links: [],
    aria: []
  };
  
  // Check images for alt text
  document.querySelectorAll('img').forEach((img, index) => {
    const alt = img.getAttribute('alt');
    if (!alt || alt.trim() === '') {
      issues.images.push({
        index: index,
        src: img.src,
        snippet: img.outerHTML.substring(0, 200)
      });
    }
  });
  
  // Check inputs for labels
  document.querySelectorAll('input').forEach((input, index) => {
    const type = (input.getAttribute('type') || '').toLowerCase();
    
    // Skip non-user-input types
    if (['hidden', 'submit', 'button', 'image', 'reset'].includes(type)) {
      return;
    }
    
    const id = input.id;
    const hasLabel = id && document.querySelector(`label[for="${id}"]`);
    const hasAriaLabel = input.getAttribute('aria-label');
    const hasAriaLabelledby = input.getAttribute('aria-labelledby');
    const wrappedInLabel = input.closest('label') !== null;
    
    if (!hasLabel && !hasAriaLabel && !hasAriaLabelledby && !wrappedInLabel) {
      issues.inputs.push({
        index: index,
        type: type,
        id: id,
        name: input.name,
        snippet: input.outerHTML.substring(0, 200)
      });
    }
  });
  
  // Check heading hierarchy
  const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
  let previousLevel = 0;
  headings.forEach((heading, index) => {
    const level = parseInt(heading.tagName.substring(1));
    if (previousLevel > 0 && level > previousLevel + 1) {
      issues.headings.push({
        index: index,
        level: level,
        previousLevel: previousLevel,
        text: heading.textContent.substring(0, 100),
        message: `Heading level skipped from h${previousLevel} to h${level}`
      });
    }
    previousLevel = level;
  });
  
  // Check links for meaningful text
  document.querySelectorAll('a').forEach((link, index) => {
    const text = link.textContent.trim().toLowerCase();
    const ariaLabel = link.getAttribute('aria-label');
    
    if (!text && !ariaLabel) {
      issues.links.push({
        index: index,
        href: link.href,
        message: 'Link has no text content',
        snippet: link.outerHTML.substring(0, 200)
      });
    } else if (['click here', 'read more', 'more', 'here'].includes(text) && !ariaLabel) {
      issues.links.push({
        index: index,
        href: link.href,
        text: text,
        message: 'Link text is not descriptive',
        snippet: link.outerHTML.substring(0, 200)
      });
    }
  });
  
  // Check for ARIA issues
  document.querySelectorAll('[role]').forEach((element, index) => {
    const role = element.getAttribute('role');
    
    // Check if interactive elements have accessible names
    if (['button', 'link', 'menuitem', 'tab'].includes(role)) {
      const hasAccessibleName = 
        element.textContent.trim() ||
        element.getAttribute('aria-label') ||
        element.getAttribute('aria-labelledby');
      
      if (!hasAccessibleName) {
        issues.aria.push({
          index: index,
          role: role,
          message: `Element with role="${role}" has no accessible name`,
          snippet: element.outerHTML.substring(0, 200)
        });
      }
    }
  });
  
  return issues;
}

// Highlight failing elements on the page
function highlightFailingElements(issuesData) {
  // Remove any existing highlights first
  removeHighlights();
  
  const highlightedElements = [];
  let errorCount = 0;
  
  // Process each category of issues
  const allElements = [];
  
  // Images
  if (issuesData.images) {
    document.querySelectorAll('img').forEach((img, index) => {
      if (issuesData.images.some(issue => issue.index === index)) {
        allElements.push({ element: img, type: 'Image Missing Alt' });
      }
    });
  }
  
  // Inputs
  if (issuesData.inputs) {
    document.querySelectorAll('input').forEach((input, index) => {
      const type = (input.getAttribute('type') || '').toLowerCase();
      if (!['hidden', 'submit', 'button', 'image', 'reset'].includes(type)) {
        if (issuesData.inputs.some(issue => issue.index === index)) {
          allElements.push({ element: input, type: 'Input Missing Label' });
        }
      }
    });
  }
  
  // Links
  if (issuesData.links) {
    document.querySelectorAll('a').forEach((link, index) => {
      if (issuesData.links.some(issue => issue.index === index)) {
        allElements.push({ element: link, type: 'Link Issue' });
      }
    });
  }
  
  // Headings
  if (issuesData.headings) {
    document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach((heading, index) => {
      if (issuesData.headings.some(issue => issue.index === index)) {
        allElements.push({ element: heading, type: 'Heading Hierarchy' });
      }
    });
  }
  
  // ARIA
  if (issuesData.aria) {
    document.querySelectorAll('[role]').forEach((element, index) => {
      if (issuesData.aria.some(issue => issue.index === index)) {
        allElements.push({ element: element, type: 'ARIA Issue' });
      }
    });
  }
  
  // Create highlights for each element
  allElements.forEach((item, index) => {
    errorCount++;
    const element = item.element;
    
    // Create highlight overlay
    const overlay = document.createElement('div');
    overlay.className = 'finaccai-error-highlight';
    overlay.setAttribute('data-finaccai-highlight', 'true');
    overlay.style.cssText = `
      position: absolute;
      border: 3px solid #ff4444;
      background: rgba(255, 68, 68, 0.15);
      pointer-events: none;
      z-index: 999999;
      box-shadow: 0 0 10px rgba(255, 68, 68, 0.5);
      transition: all 0.3s ease;
    `;
    
    // Create error badge
    const badge = document.createElement('div');
    badge.className = 'finaccai-error-badge';
    badge.setAttribute('data-finaccai-highlight', 'true');
    badge.textContent = errorCount.toString();
    badge.title = item.type;
    badge.style.cssText = `
      position: absolute;
      top: -12px;
      left: -12px;
      width: 24px;
      height: 24px;
      background: #ff4444;
      color: white;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      font-size: 12px;
      font-family: Arial, sans-serif;
      box-shadow: 0 2px 4px rgba(0,0,0,0.3);
      z-index: 1000000;
    `;
    
    // Position the overlay
    const rect = element.getBoundingClientRect();
    overlay.style.top = (rect.top + window.scrollY) + 'px';
    overlay.style.left = (rect.left + window.scrollX) + 'px';
    overlay.style.width = Math.max(rect.width, 20) + 'px';
    overlay.style.height = Math.max(rect.height, 20) + 'px';
    
    overlay.appendChild(badge);
    document.body.appendChild(overlay);
    
    highlightedElements.push(overlay);
  });
  
  return highlightedElements;
}

// Remove all highlights
function removeHighlights() {
  const highlights = document.querySelectorAll('[data-finaccai-highlight="true"]');
  highlights.forEach(h => h.remove());
}

// Capture element with context for screenshot
function captureElementContext(element) {
  try {
    const rect = element.getBoundingClientRect();
    const scrollLeft = window.scrollX || window.pageXOffset;
    const scrollTop = window.scrollY || window.pageYOffset;
    
    return {
      top: rect.top + scrollTop - 50,      // Add 50px context above
      left: Math.max(0, rect.left + scrollLeft - 50),
      width: rect.width + 100,             // Add 50px context on each side
      height: rect.height + 100,
      elementTop: rect.top + scrollTop,
      elementLeft: rect.left + scrollLeft,
      elementWidth: rect.width,
      elementHeight: rect.height
    };
  } catch (e) {
    return null;
  }
}

// Scroll to element and return coords
function scrollToElement(element) {
  try {
    element.scrollIntoView({ behavior: 'auto', block: 'center' });
    return new Promise(resolve => {
      setTimeout(() => {
        const rect = element.getBoundingClientRect();
        resolve({
          scrolled: true,
          rect: rect
        });
      }, 500);
    });
  } catch (e) {
    return Promise.resolve({ scrolled: false });
  }
}

// Listen for highlight requests
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'highlightElements') {
    try {
      highlightFailingElements(request.issues);
      sendResponse({ success: true });
    } catch (error) {
      sendResponse({ success: false, error: error.toString() });
    }
    return true;
  }
  
  if (request.action === 'removeHighlights') {
    try {
      removeHighlights();
      sendResponse({ success: true });
    } catch (error) {
      sendResponse({ success: false, error: error.toString() });
    }
    return true;
  }
  
  if (request.action === 'scrollToElement') {
    try {
      const element = document.querySelector(request.selector);
      if (element) {
        scrollToElement(element).then(result => {
          sendResponse({ success: true, ...result });
        });
      } else {
        sendResponse({ success: false, error: 'Element not found' });
      }
    } catch (error) {
      sendResponse({ success: false, error: error.toString() });
    }
    return true;
  }
  
  if (request.action === 'getPageDimensions') {
    try {
      sendResponse({
        width: window.innerWidth,
        height: document.documentElement.scrollHeight,
        scrollHeight: document.body.scrollHeight
      });
    } catch (error) {
      sendResponse({ error: error.toString() });
    }
    return true;
  }
  
  // Capture full page screenshot by stitching viewport captures
  if (request.action === 'captureFullPageScreenshot') {
    captureFullPage()
      .then(dataUrl => sendResponse({ success: true, screenshot: dataUrl }))
      .catch(error => sendResponse({ success: false, error: error.toString() }));
    return true;
  }
  
  // Execute arbitrary script
  if (request.action === 'executeScript') {
    try {
      eval(request.script);
      sendResponse({ success: true });
    } catch (error) {
      sendResponse({ success: false, error: error.toString() });
    }
    return true;
  }
});

// Capture full page screenshot
async function captureFullPage() {
  const originalScrollY = window.scrollY;
  const originalScrollX = window.scrollX;
  
  try {
    // Get page dimensions
    const pageHeight = Math.max(
      document.body.scrollHeight,
      document.documentElement.scrollHeight,
      document.body.offsetHeight,
      document.documentElement.offsetHeight,
      document.body.clientHeight,
      document.documentElement.clientHeight
    );
    
    const pageWidth = Math.max(
      document.body.scrollWidth,
      document.documentElement.scrollWidth,
      document.body.offsetWidth,
      document.documentElement.offsetWidth,
      document.body.clientWidth,
      document.documentElement.clientWidth
    );
    
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;
    
    // For now, return a message that full stitching requires backend
    // The extension will capture visible viewport with highlights
    window.scrollTo(0, 0);
    await new Promise(resolve => setTimeout(resolve, 100));
    
    return {
      needsStitching: true,
      pageHeight,
      pageWidth,
      viewportHeight,
      viewportWidth,
      message: 'Full page screenshot will be captured by extension API'
    };
    
  } finally {
    // Restore original scroll position
    window.scrollTo(originalScrollX, originalScrollY);
  }
}

// Inject a notification when the extension is ready
console.log('FinACCAI Accessibility Checker is ready');
