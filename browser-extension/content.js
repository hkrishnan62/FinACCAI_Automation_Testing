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

// Inject a notification when the extension is ready
console.log('FinACCAI Accessibility Checker is ready');
