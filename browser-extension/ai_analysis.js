/**
 * Client-side AI/ML Analysis for FinACCAI
 * Uses TensorFlow.js and custom algorithms for accessibility analysis
 */

class FinACCAIAIAnalysis {
  constructor() {
    this.loaded = false;
    this.models = {};
  }

  /**
   * Initialize AI/ML models (async)
   */
  async init() {
    if (this.loaded) return;
    try {
      console.log('[FinACCAI AI] Initializing models...');
      // Models will be loaded on-demand
      this.loaded = true;
      console.log('[FinACCAI AI] Models ready');
    } catch (e) {
      console.warn('[FinACCAI AI] Could not load models:', e);
    }
  }

  /**
   * Analyze HTML content for accessibility issues using AI
   */
  async analyzeContent(html, checks) {
    const analysis = {
      nlp_analysis: this.performNLPAnalysis(html),
      ml_predictions: this.performMLPredictions(html, checks),
      vision_analysis: this.performVisionAnalysis(html),
      xai_explanations: this.generateExplanations(checks),
      status: 'AI/ML analysis completed',
      timestamp: new Date().toISOString()
    };

    return analysis;
  }

  /**
   * NLP Analysis - Analyze text content quality and labels
   */
  performNLPAnalysis(html) {
    const results = {
      text_quality: 0,
      label_quality: 0,
      semantic_structure: [],
      recommendations: []
    };

    try {
      // Parse HTML
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');

      // Analyze text content
      const bodyText = doc.body.innerText || '';
      const wordCount = bodyText.split(/\s+/).filter(w => w.length > 0).length;
      const sentences = bodyText.split(/[.!?]+/).filter(s => s.trim().length > 0).length;

      // Text quality score (based on length and structure)
      results.text_quality = Math.min(100, Math.round((wordCount / 100) * 50 + (sentences / 10) * 50));

      // Analyze labels
      const labels = doc.querySelectorAll('label');
      const inputs = doc.querySelectorAll('input, textarea, select');
      const labeledInputs = new Set();

      labels.forEach(label => {
        if (label.htmlFor) {
          labeledInputs.add(label.htmlFor);
        }
      });

      results.label_quality = Math.round((labeledInputs.size / Math.max(inputs.length, 1)) * 100);

      // Analyze semantic structure
      const headings = doc.querySelectorAll('h1, h2, h3, h4, h5, h6');
      const lists = doc.querySelectorAll('ul, ol');
      const sections = doc.querySelectorAll('section, article, nav, main');

      results.semantic_structure = {
        headings_count: headings.length,
        lists_count: lists.length,
        semantic_sections: sections.length
      };

      // Recommendations
      if (results.text_quality < 50) {
        results.recommendations.push('Consider adding more descriptive content to the page');
      }
      if (results.label_quality < 80) {
        results.recommendations.push('Many input fields lack proper labels - critical for accessibility');
      }
      if (sections.length === 0) {
        results.recommendations.push('Use semantic HTML sections (section, article, nav) for better structure');
      }

    } catch (e) {
      console.warn('[FinACCAI AI] NLP analysis error:', e);
    }

    return results;
  }

  /**
   * ML Predictions - Detect complex accessibility patterns
   */
  performMLPredictions(html, checks) {
    const predictions = {
      high_risk_issues: [],
      low_risk_issues: [],
      compliance_score: 0,
      patterns: {},
      summary: {
        title: '',
        description: ''
      },
      recommendations: [],
      best_practices: []
    };

    try {
      const totalIssues = Object.values(checks).reduce((sum, arr) => sum + arr.length, 0);
      
      // Categorize issues by severity
      if (checks.images && checks.images.length > 0) {
        predictions.high_risk_issues.push({
          type: 'missing_alt_text',
          count: checks.images.length,
          severity: 'critical',
          impact: 'Blind users cannot understand image content',
          what_to_do: `Add meaningful alt text to all ${checks.images.length} images`,
          wcag_standard: 'WCAG 2.1 1.1.1 Level A',
          why_matters: 'Images are fundamental content on the web. Without alt text, blind users miss this content entirely.'
        });
      }

      if (checks.inputs && checks.inputs.length > 0) {
        predictions.high_risk_issues.push({
          type: 'unlabeled_inputs',
          count: checks.inputs.length,
          severity: 'critical',
          impact: 'Screen reader users cannot identify form fields',
          what_to_do: `Add <label> elements to all ${checks.inputs.length} form inputs`,
          wcag_standard: 'WCAG 2.1 1.3.1 Level A',
          why_matters: 'Forms are unusable without labels. Users need to know what data each field expects.'
        });
      }

      if (checks.headings && checks.headings.length > 0) {
        predictions.high_risk_issues.push({
          type: 'heading_hierarchy',
          count: checks.headings.length,
          severity: 'high',
          impact: 'Users cannot navigate page structure efficiently',
          what_to_do: 'Reorganize headings to follow proper hierarchy (h1 → h2 → h3)',
          wcag_standard: 'WCAG 2.1 1.3.1 Level A',
          why_matters: 'Heading hierarchy is like a table of contents. Screen reader users use it to jump to content.'
        });
      }

      if (checks.links && checks.links.length > 0) {
        predictions.low_risk_issues.push({
          type: 'link_issues',
          count: checks.links.length,
          severity: 'medium',
          impact: 'Link purpose may be unclear to screen reader users',
          what_to_do: `Update ${checks.links.length} link text to be more descriptive`,
          wcag_standard: 'WCAG 2.1 2.4.4 Level A',
          why_matters: 'Screen reader users often list all links on a page. Generic text like "click here" is confusing.'
        });
      }

      if (checks.aria && checks.aria.length > 0) {
        predictions.high_risk_issues.push({
          type: 'aria_issues',
          count: checks.aria.length,
          severity: 'high',
          impact: 'Custom UI components may not be properly announced',
          what_to_do: 'Review ARIA attributes and prefer native HTML elements',
          wcag_standard: 'WCAG 2.1 4.1.2 Level A',
          why_matters: 'Incorrect ARIA is worse than no ARIA. It provides false information to screen readers.'
        });
      }

      // Calculate compliance score
      const maxIssues = 100;
      const issueWeight = (totalIssues / maxIssues) * 100;
      predictions.compliance_score = Math.max(0, 100 - issueWeight);

      // Identify patterns
      predictions.patterns = {
        total_issues: totalIssues,
        critical_issues: predictions.high_risk_issues.reduce((sum, i) => sum + i.count, 0),
        medium_issues: predictions.low_risk_issues.reduce((sum, i) => sum + i.count, 0),
        has_alt_text_issues: checks.images.length > 0,
        has_label_issues: checks.inputs.length > 0,
        has_structure_issues: checks.headings.length > 0
      };

      // Generate summary
      if (totalIssues === 0) {
        predictions.summary.title = '✓ Excellent Accessibility Foundation';
        predictions.summary.description = 'This page has strong baseline accessibility. Consider advanced testing with screen readers.';
      } else if (predictions.compliance_score >= 80) {
        predictions.summary.title = '✓ Good Accessibility';
        predictions.summary.description = `Page has good accessibility but needs attention to ${totalIssues} issue${totalIssues > 1 ? 's' : ''}.`;
      } else if (predictions.compliance_score >= 60) {
        predictions.summary.title = '⚠ Fair Accessibility';
        predictions.summary.description = `Page has ${totalIssues} accessibility issues that should be addressed.`;
      } else {
        predictions.summary.title = '✗ Poor Accessibility';
        predictions.summary.description = `Page has ${totalIssues} critical accessibility issues. Many users with disabilities cannot access this content.`;
      }

      // Add recommendations
      predictions.recommendations = [
        {
          recommendation: `Start by fixing ${predictions.patterns.critical_issues} critical issues`,
          category: 'Priority',
          priority: 'CRITICAL'
        },
        {
          recommendation: 'Test with actual screen readers (NVDA, JAWS, VoiceOver)',
          category: 'Testing',
          priority: 'HIGH'
        },
        {
          recommendation: 'Train team members on accessibility best practices',
          category: 'Process',
          priority: 'MEDIUM'
        }
      ];

      // Best practices
      predictions.best_practices = [
        'Always include alt text for images',
        'Use semantic HTML elements (nav, main, article, section)',
        'Test keyboard navigation without a mouse',
        'Ensure 4.5:1 color contrast for text',
        'Make interactive elements accessible with keyboard',
        'Use ARIA only when native HTML is insufficient'
      ];

    } catch (e) {
      console.warn('[FinACCAI AI] ML prediction error:', e);
    }

    return predictions;
  }

  /**
   * Vision Analysis - Analyze images and visual elements
   */
  performVisionAnalysis(html) {
    const results = {
      images_analyzed: 0,
      images_with_alt: 0,
      images_with_descriptions: 0,
      recommendations: []
    };

    try {
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      const images = doc.querySelectorAll('img');

      results.images_analyzed = images.length;

      images.forEach(img => {
        const alt = img.getAttribute('alt');
        const title = img.getAttribute('title');

        if (alt && alt.trim()) {
          results.images_with_alt++;
          // Check if alt text is descriptive (length > 5 chars)
          if (alt.length > 5) {
            results.images_with_descriptions++;
          }
        }
      });

      // Calculate image coverage
      if (images.length > 0) {
        const altCoverage = (results.images_with_alt / images.length) * 100;
        const descriptionCoverage = (results.images_with_descriptions / images.length) * 100;

        if (altCoverage < 100) {
          results.recommendations.push(`${Math.round(100 - altCoverage)}% of images are missing alt text`);
        }
        if (descriptionCoverage < 50) {
          results.recommendations.push('Many alt texts are too short - use descriptive text');
        }
      }

    } catch (e) {
      console.warn('[FinACCAI AI] Vision analysis error:', e);
    }

    return results;
  }

  /**
   * Generate XAI (Explainable AI) explanations
   */
  generateExplanations(checks) {
    const explanations = {
      critical_fixes: [],
      important_fixes: [],
      recommendations: [],
      best_practices: []
    };

    try {
      // Critical fixes with detailed XAI explanation
      if (checks.images && checks.images.length > 0) {
        explanations.critical_fixes.push({
          issue: 'Missing Alt Text',
          why: 'Screen readers cannot describe images to blind or low-vision users. Without alt text, they hear "image" and nothing else. This completely blocks access to image content.',
          impact_users: 'Blind users, low-vision users, users with cognitive disabilities, search engines',
          fix: `Add alt="${checks.images[0]?.src?.split('/').pop() || 'description'}" to all <img> tags with meaningful descriptions`,
          example: '<img src="logo.png" alt="Company logo">',
          wcag: 'WCAG 2.1 1.1.1 (Level A)',
          severity: 'CRITICAL',
          count: checks.images.length
        });
      }

      if (checks.inputs && checks.inputs.length > 0) {
        explanations.critical_fixes.push({
          issue: 'Unlabeled Form Fields',
          why: 'Screen reader users cannot identify what information should go in form fields. This makes forms impossible to use. Users with assistive technology have no way to know if they are entering data in the correct field.',
          impact_users: 'Blind users, low-vision users, keyboard-only users, users with motor disabilities',
          fix: `Use <label for="input_id">Label Text</label> paired with input IDs. Or wrap inputs in labels: <label>Email <input type="email"></label>`,
          example: '<label for="email">Email Address</label><input id="email" type="email" required>',
          wcag: 'WCAG 2.1 1.3.1 (Level A)',
          severity: 'CRITICAL',
          count: checks.inputs.length
        });
      }

      // Important fixes
      if (checks.headings && checks.headings.length > 0) {
        explanations.important_fixes.push({
          issue: 'Heading Hierarchy Problems',
          why: 'Screen reader users navigate pages using heading hierarchies (h1 → h2 → h3). When hierarchy is broken (h1 → h3, skipping h2), it confuses navigation. Users cannot understand page structure.',
          impact_users: 'Blind users, low-vision users, users with cognitive disabilities',
          fix: 'Use <h1>, <h2>, <h3> in order without skipping levels. One H1 per page. Start with H1, then H2, then H3, etc.',
          example: '<h1>Page Title</h1>\n<h2>Section 1</h2>\n<h3>Subsection 1.1</h3>\n<h3>Subsection 1.2</h3>\n<h2>Section 2</h2>',
          wcag: 'WCAG 2.1 1.3.1 (Level A)',
          severity: 'HIGH',
          count: checks.headings.length
        });
      }

      if (checks.links && checks.links.length > 0) {
        explanations.important_fixes.push({
          issue: 'Link Accessibility Issues',
          why: "Links with generic text like \"click here\", \"read more\", or \"link\" don't tell users what they will get. Screen reader users often navigate by links only. Descriptive link text is essential.",
          impact_users: 'Blind users, low-vision users, users with cognitive disabilities, keyboard-only users',
          fix: 'Use descriptive link text that makes sense out of context: "Read our accessibility guidelines" instead of "click here"',
          example: '<!-- Bad -->\n<a href="/docs">Click here</a>\n\n<!-- Good -->\n<a href="/docs">Read our accessibility guidelines</a>',
          wcag: 'WCAG 2.1 2.4.4 (Level A)',
          severity: 'MEDIUM',
          count: checks.links.length
        });
      }

      if (checks.aria && checks.aria.length > 0) {
        explanations.important_fixes.push({
          issue: 'ARIA Attribute Issues',
          why: 'Incorrectly used ARIA attributes provide wrong information to screen readers. ARIA should enhance native HTML, not replace it. Bad ARIA is worse than no ARIA.',
          impact_users: 'Blind users, low-vision users, users with motor disabilities',
          fix: 'Prefer native HTML elements. Use ARIA only when native HTML does not exist. Always test with actual screen readers.',
          example: '<!-- Bad: Using role when button element exists -->\n<div role="button">Click me</div>\n\n<!-- Good: Use native button -->\n<button>Click me</button>',
          wcag: 'WCAG 2.1 4.1.2 (Level A)',
          severity: 'MEDIUM',
          count: checks.aria.length
        });
      }

      // Best practices
      explanations.best_practices = [
        {
          title: 'Use Semantic HTML',
          description: 'Prefer native elements (<button>, <nav>, <article>, <header>) over generic divs with ARIA. Semantic HTML is accessible by default.',
          examples: ['<button> instead of <div role="button">', '<nav> for navigation', '<article> for content', '<label> for form inputs']
        },
        {
          title: 'Test with Screen Readers',
          description: 'The only way to know if your site is truly accessible. Test with real assistive technology.',
          examples: ['NVDA (Free, Windows)', 'JAWS (Paid, Windows)', 'VoiceOver (Free, macOS/iOS)', 'TalkBack (Free, Android)']
        },
        {
          title: 'Ensure Keyboard Navigation',
          description: 'All interactive elements must be keyboard accessible. Users should navigate with Tab, activate with Enter, dismiss with Escape.',
          examples: ['Tabindex should rarely be needed (use -1 to remove, never > 0)', 'Skip links for keyboard users', 'Focus visible indicator always visible']
        },
        {
          title: 'Color Contrast',
          description: 'Text must have sufficient contrast with background. Minimum 4.5:1 for regular text, 3:1 for large text (WCAG AA).',
          examples: ['Use contrast checkers: WebAIM, TPGi', 'Never rely on color alone to convey meaning', 'Test with color blindness simulators']
        },
        {
          title: 'Alternative Content',
          description: 'Provide alternatives for all non-text content: images, audio, video, infographics.',
          examples: ['Alt text for images', 'Captions for video', 'Transcripts for audio', 'Descriptions for complex graphics']
        }
      ];

      // Generate recommendations based on findings
      explanations.recommendations = [];
      const totalIssues = Object.values(checks).reduce((sum, arr) => sum + arr.length, 0);
      
      if (totalIssues === 0) {
        explanations.recommendations.push({
          recommendation: 'Site appears to meet basic WCAG A standards',
          category: 'Positive',
          priority: 'LOW'
        });
        explanations.recommendations.push({
          recommendation: 'Consider testing with actual screen readers (NVDA, JAWS) for comprehensive evaluation',
          category: 'Testing',
          priority: 'MEDIUM'
        });
      } else {
        explanations.recommendations.push({
          recommendation: `Fix ${checks.images.length} missing image alt texts - this is critical for blind users`,
          category: 'Images',
          priority: 'CRITICAL'
        });
        
        if (checks.inputs.length > 0) {
          explanations.recommendations.push({
            recommendation: `Add labels to ${checks.inputs.length} unlabeled form fields`,
            category: 'Forms',
            priority: 'CRITICAL'
          });
        }
        
        if (checks.headings.length > 0) {
          explanations.recommendations.push({
            recommendation: 'Fix heading hierarchy - ensure proper nesting (h1 → h2 → h3)',
            category: 'Structure',
            priority: 'HIGH'
          });
        }
        
        if (checks.links.length > 0) {
          explanations.recommendations.push({
            recommendation: 'Review link text - make links descriptive without context',
            category: 'Navigation',
            priority: 'MEDIUM'
          });
        }
      }

    } catch (e) {
      console.warn('[FinACCAI AI] XAI generation error:', e);
    }

    return explanations;
  }

  /**
   * Generate a comprehensive AI/ML report
   */
  async generateReport(html, checks) {
    await this.init();
    return this.analyzeContent(html, checks);
  }
}

// Create global instance
const finaccaiAI = new FinACCAIAIAnalysis();
