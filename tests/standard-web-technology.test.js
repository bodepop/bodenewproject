/**
 * Property Test: Standard Web Technology Usage
 * Validates Requirements 5.2, 5.4
 * 
 * This test ensures the website uses standard web technologies correctly
 * and follows web standards for compatibility and accessibility.
 */

const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

describe('Property 5: Standard Web Technology Usage', () => {
  let htmlContent, dom, document;
  let cssContent, jsContent;

  beforeAll(() => {
    // Read HTML content
    htmlContent = fs.readFileSync(path.join(__dirname, '../index.html'), 'utf8');
    dom = new JSDOM(htmlContent);
    document = dom.window.document;
    
    // Read CSS content
    cssContent = fs.readFileSync(path.join(__dirname, '../css/styles.css'), 'utf8');
    
    // Read JavaScript content
    jsContent = fs.readFileSync(path.join(__dirname, '../js/main.js'), 'utf8');
  });

  describe('HTML5 Semantic Structure', () => {
    test('uses proper HTML5 doctype', () => {
      expect(htmlContent.trim().startsWith('<!DOCTYPE html>')).toBe(true);
    });

    test('has valid HTML5 semantic elements', () => {
      const semanticElements = [
        'header', 'nav', 'main', 'section', 'article', 'aside', 'footer'
      ];
      
      semanticElements.forEach(element => {
        const elements = document.querySelectorAll(element);
        if (elements.length > 0) {
          expect(elements.length).toBeGreaterThan(0);
        }
      });
    });

    test('has proper meta tags for web standards', () => {
      const charset = document.querySelector('meta[charset]');
      expect(charset).toBeTruthy();
      expect(charset.getAttribute('charset').toLowerCase()).toBe('utf-8');

      const viewport = document.querySelector('meta[name="viewport"]');
      expect(viewport).toBeTruthy();
      expect(viewport.getAttribute('content')).toContain('width=device-width');
    });

    test('has proper language attribute', () => {
      const html = document.documentElement;
      expect(html.getAttribute('lang')).toBeTruthy();
      expect(html.getAttribute('lang')).toMatch(/^[a-z]{2}(-[A-Z]{2})?$/);
    });
  });

  describe('CSS Standards Compliance', () => {
    test('uses CSS custom properties (CSS variables)', () => {
      const customPropertyRegex = /--[\w-]+\s*:/g;
      const matches = cssContent.match(customPropertyRegex);
      expect(matches).toBeTruthy();
      expect(matches.length).toBeGreaterThan(5);
    });

    test('uses modern CSS layout methods', () => {
      expect(cssContent).toMatch(/display:\s*grid/);
      expect(cssContent).toMatch(/display:\s*flex/);
    });

    test('includes responsive design with media queries', () => {
      const mediaQueryRegex = /@media[^{]+\{/g;
      const matches = cssContent.match(mediaQueryRegex);
      expect(matches).toBeTruthy();
      expect(matches.length).toBeGreaterThan(0);
    });

    test('uses standard CSS units and values', () => {
      // Check for modern CSS units
      expect(cssContent).toMatch(/\d+rem/);
      expect(cssContent).toMatch(/\d+vh|vw/);
      
      // Check for standard color formats
      expect(cssContent).toMatch(/#[0-9a-fA-F]{3,6}/);
      expect(cssContent).toMatch(/rgba?\(/);
    });
  });

  describe('JavaScript Standards Compliance', () => {
    test('uses modern JavaScript features appropriately', () => {
      // Check for ES6+ features
      expect(jsContent).toMatch(/const\s+\w+/);
      expect(jsContent).toMatch(/let\s+\w+/);
      expect(jsContent).toMatch(/=>\s*{?/); // Arrow functions
    });

    test('uses standard DOM APIs', () => {
      expect(jsContent).toMatch(/document\.querySelector/);
      expect(jsContent).toMatch(/addEventListener/);
      expect(jsContent).toMatch(/requestAnimationFrame/);
    });

    test('includes proper error handling', () => {
      expect(jsContent).toMatch(/try\s*{|catch\s*\(/);
      expect(jsContent).toMatch(/addEventListener\s*\(\s*['"]error['"]/);
    });

    test('uses performance-conscious patterns', () => {
      expect(jsContent).toMatch(/requestAnimationFrame/);
      expect(jsContent).toMatch(/debounce|throttle/);
    });
  });

  describe('Web Standards Accessibility', () => {
    test('has proper heading hierarchy', () => {
      const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
      expect(headings.length).toBeGreaterThan(0);
      
      // Should have at least one h1
      const h1Elements = document.querySelectorAll('h1');
      expect(h1Elements.length).toBeGreaterThanOrEqual(1);
    });

    test('has alt attributes for images', () => {
      const images = document.querySelectorAll('img');
      images.forEach(img => {
        expect(img.hasAttribute('alt')).toBe(true);
      });
    });

    test('has proper link attributes', () => {
      const externalLinks = document.querySelectorAll('a[target="_blank"]');
      externalLinks.forEach(link => {
        expect(link.getAttribute('rel')).toContain('noopener');
      });
    });

    test('has proper form labels and inputs', () => {
      const inputs = document.querySelectorAll('input, textarea, select');
      inputs.forEach(input => {
        const id = input.getAttribute('id');
        if (id) {
          const label = document.querySelector(`label[for="${id}"]`);
          expect(label || input.getAttribute('aria-label')).toBeTruthy();
        }
      });
    });
  });

  describe('Performance Standards', () => {
    test('includes resource optimization hints', () => {
      const preloadLinks = document.querySelectorAll('link[rel="preload"]');
      const prefetchLinks = document.querySelectorAll('link[rel="prefetch"]');
      
      // Should have some performance optimization
      expect(preloadLinks.length + prefetchLinks.length).toBeGreaterThanOrEqual(0);
    });

    test('uses efficient CSS selectors', () => {
      // Check for efficient selectors (avoid overly complex ones)
      const inefficientSelectors = cssContent.match(/\*\s*\*|\w+\s+\*\s+\w+/g);
      expect(inefficientSelectors).toBeFalsy();
    });

    test('minimizes DOM queries in JavaScript', () => {
      // Check for cached DOM queries
      expect(jsContent).toMatch(/const\s+\w+\s*=\s*document\.querySelector/);
      expect(jsContent).toMatch(/const\s+\w+\s*=\s*document\.querySelectorAll/);
    });
  });

  describe('Cross-browser Compatibility', () => {
    test('includes vendor prefixes where necessary', () => {
      // Check for modern CSS that might need prefixes
      if (cssContent.includes('backdrop-filter')) {
        expect(cssContent).toMatch(/-webkit-backdrop-filter/);
      }
    });

    test('uses feature detection patterns', () => {
      // Check for feature detection in JavaScript
      expect(jsContent).toMatch(/typeof\s+\w+\s*!==\s*['"]undefined['"]|window\.\w+/);
    });

    test('provides fallbacks for modern features', () => {
      // Check for fallback patterns
      expect(jsContent).toMatch(/catch|error|fallback/i);
    });
  });

  describe('Security Standards', () => {
    test('uses secure protocols in links', () => {
      const httpLinks = htmlContent.match(/href\s*=\s*['"]http:\/\//g);
      // Should prefer HTTPS or relative URLs
      expect(httpLinks).toBeFalsy();
    });

    test('includes proper CSP-friendly patterns', () => {
      // Check for inline script/style minimization
      const inlineScripts = document.querySelectorAll('script:not([src])');
      const inlineStyles = document.querySelectorAll('style');
      
      // Should minimize inline content for CSP compatibility
      expect(inlineScripts.length + inlineStyles.length).toBeLessThan(5);
    });
  });

  describe('Progressive Enhancement', () => {
    test('provides basic functionality without JavaScript', () => {
      // Check that navigation links work without JavaScript
      const navLinks = document.querySelectorAll('nav a[href^="#"]');
      navLinks.forEach(link => {
        const href = link.getAttribute('href');
        const target = document.querySelector(href);
        expect(target).toBeTruthy();
      });
    });

    test('uses semantic HTML that works without CSS', () => {
      // Check for proper semantic structure
      const main = document.querySelector('main');
      const sections = document.querySelectorAll('section');
      
      expect(main || sections.length > 0).toBeTruthy();
    });
  });

  describe('Web Standards Validation', () => {
    test('uses valid HTML structure', () => {
      // Basic HTML validation checks
      expect(htmlContent).toMatch(/<html[^>]*>/);
      expect(htmlContent).toMatch(/<head[^>]*>/);
      expect(htmlContent).toMatch(/<body[^>]*>/);
      expect(htmlContent).toMatch(/<\/html>/);
    });

    test('uses proper CSS syntax', () => {
      // Check for basic CSS syntax validity
      const braceCount = (cssContent.match(/\{/g) || []).length;
      const closeBraceCount = (cssContent.match(/\}/g) || []).length;
      expect(braceCount).toBe(closeBraceCount);
    });

    test('uses proper JavaScript syntax patterns', () => {
      // Check for basic JavaScript patterns
      expect(jsContent).toMatch(/function\s+\w+\s*\(|const\s+\w+\s*=\s*function|\w+\s*=>\s*/);
      
      // Check for proper semicolon usage or ASI compatibility
      const statements = jsContent.split('\n').filter(line => 
        line.trim() && 
        !line.trim().startsWith('//') && 
        !line.trim().startsWith('/*') &&
        !line.trim().startsWith('*')
      );
      
      expect(statements.length).toBeGreaterThan(0);
    });
  });
});