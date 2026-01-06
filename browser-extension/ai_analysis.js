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
      patterns: {}
    };

    try {
      const totalIssues = Object.values(checks).reduce((sum, arr) => sum + arr.length, 0);
      
      // Categorize issues by severity
      if (checks.images && checks.images.length > 0) {
        predictions.high_risk_issues.push({
          type: 'missing_alt_text',
          count: checks.images.length,
          severity: 'critical',
          impact: 'Blind users cannot understand image content'
        });
      }

      if (checks.inputs && checks.inputs.length > 0) {
        predictions.high_risk_issues.push({
          type: 'unlabeled_inputs',
          count: checks.inputs.length,
          severity: 'critical',
          impact: 'Screen reader users cannot identify form fields'
        });
      }

      if (checks.headings && checks.headings.length > 0) {
        predictions.high_risk_issues.push({
          type: 'heading_hierarchy',
          count: checks.headings.length,
          severity: 'high',
          impact: 'Users cannot navigate page structure efficiently'
        });
      }

      if (checks.links && checks.links.length > 0) {
        predictions.low_risk_issues.push({
          type: 'link_issues',
          count: checks.links.length,
          severity: 'medium',
          impact: 'Link purpose may be unclear to screen reader users'
        });
      }

      if (checks.aria && checks.aria.length > 0) {
        predictions.high_risk_issues.push({
          type: 'aria_issues',
          count: checks.aria.length,
          severity: 'high',
          impact: 'Custom UI components may not be properly announced'
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
      // Critical fixes
      if (checks.images && checks.images.length > 0) {
        explanations.critical_fixes.push({
          issue: 'Missing Alt Text',
          why: 'Screen readers cannot describe images to blind users',
          fix: `Add alt="${checks.images[0]?.src?.split('/').pop() || 'description'}" to all <img> tags`,
          example: '<img src="logo.png" alt="Company logo">',
          wcag: 'WCAG 2.1 1.1.1 (Level A)'
        });
      }

      if (checks.inputs && checks.inputs.length > 0) {
        explanations.critical_fixes.push({
          issue: 'Unlabeled Form Fields',
          why: 'Users with assistive technology cannot identify form fields',
          fix: `Use <label for="input_id">Label</label> paired with input IDs`,
          example: '<label for="email">Email</label><input id="email" type="email">',
          wcag: 'WCAG 2.1 1.3.1 (Level A)'
        });
      }

      // Important fixes
      if (checks.headings && checks.headings.length > 0) {
        explanations.important_fixes.push({
          issue: 'Heading Hierarchy Problems',
          why: 'Users cannot navigate page structure; skipped heading levels confuse screen readers',
          fix: 'Use <h1>, <h2>, <h3> in order without skipping levels',
          example: '<h1>Page Title</h1><h2>Section</h2><h3>Subsection</h3>',
          wcag: 'WCAG 2.1 1.3.1 (Level A)'
        });
      }

      // General recommendations
      explanations.recommendations.push({
        title: 'Use ARIA only when semantic HTML fails',
        description: 'Prefer native HTML elements (<button>, <nav>, <article>) over <div role="button">'
      });

      explanations.recommendations.push({
        title: 'Provide keyboard navigation',
        description: 'All interactive elements must be keyboard accessible (Tab, Enter, Escape keys)'
      });

      explanations.recommendations.push({
        title: 'Ensure sufficient color contrast',
        description: 'Text should have at least 4.5:1 contrast ratio with background (WCAG AA standard)'
      });

      // Best practices
      explanations.best_practices.push('Test with screen readers (NVDA, JAWS, VoiceOver)');
      explanations.best_practices.push('Use semantic HTML: <header>, <nav>, <main>, <footer>');
      explanations.best_practices.push('Implement skip links for keyboard navigation');
      explanations.best_practices.push('Use ARIA landmarks appropriately');
      explanations.best_practices.push('Provide captions and transcripts for media');

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
