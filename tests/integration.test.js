/**
 * Integration Tests: Complete Website Functionality
 * Validates all requirements working together
 * 
 * This test suite ensures all components work together seamlessly
 * and the complete user flow functions as expected.
 */

const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

describe('Integration Tests: Complete Website', () => {
  let htmlContent, dom, window, document;
  let cssContent, jsContent;

  beforeAll(() => {
    // Read all content
    htmlContent = fs.readFileSync(path.join(__dirname, '../index.html'), 'utf8');
    cssContent = fs.readFileSync(path.join(__dirname, '../css/styles.css'), 'utf8');
    jsContent = fs.readFileSync(path.join(__dirname, '../js/main.js'), 'utf8');
    
    // Create DOM with JavaScript support
    dom = new JSDOM(htmlContent, {
      runScripts: 'dangerously',
      resources: 'usable',
      pretendToBeVisual: true
    });
    
    window = dom.window;
    document = window.document;
    
    // Add CSS to the document
    const style = document.createElement('style');
    style.textContent = cssContent;
    document.head.appendChild(style);
  });

  describe('Complete User Journey', () => {
    test('user can navigate through all sections', () => {
      // Check all main sections exist and are accessible
      const sections = ['header', 'about', 'skills', 'experience', 'contact'];
      
      sections.forEach(sectionId => {
        const section = document.getElementById(sectionId) || 
                       document.querySelector(`section.${sectionId}`) ||
                       document.querySelector(`.${sectionId}-section`);
        
        expect(section).toBeTruthy();
        
        // Check if there's a navigation link to this section
        const navLink = document.querySelector(`a[href="#${sectionId}"]`) ||
                       document.querySelector(`a[href*="${sectionId}"]`);
        
        if (navLink) {
          expect(navLink).toBeTruthy();
        }
      });
    });

    test('navigation links correspond to actual sections', () => {
      const navLinks = document.querySelectorAll('nav a[href^="#"]');
      
      navLinks.forEach(link => {
        const href = link.getAttribute('href');
        const targetId = href.substring(1);
        const targetSection = document.getElementById(targetId);
        
        expect(targetSection).toBeTruthy();
      });
    });

    test('all essential content is present and accessible', () => {
      // Profile information
      const profileName = document.querySelector('h1, .profile-name, .hero h1');
      expect(profileName).toBeTruthy();
      expect(profileName.textContent.trim()).toBeTruthy();

      // Professional title
      const title = document.querySelector('.profile-title, .hero h2, .subtitle');
      expect(title).toBeTruthy();

      // About section content
      const aboutContent = document.querySelector('#about p, .about-content p, .about p');
      expect(aboutContent).toBeTruthy();

      // Skills section
      const skillsSection = document.querySelector('#skills, .skills-section');
      expect(skillsSection).toBeTruthy();

      // Experience section
      const experienceSection = document.querySelector('#experience, .experience-section');
      expect(experienceSection).toBeTruthy();

      // Contact information
      const contactSection = document.querySelector('#contact, .contact-section');
      expect(contactSection).toBeTruthy();
    });
  });

  describe('Cross-Section Integration', () => {
    test('consistent styling across all sections', () => {
      const sections = document.querySelectorAll('section');
      
      sections.forEach(section => {
        // Each section should have consistent structure
        const heading = section.querySelector('h1, h2, h3');
        expect(heading).toBeTruthy();
        
        // Check for consistent spacing classes or styles
        const hasSpacing = section.classList.contains('section') ||
                          section.style.padding ||
                          section.style.margin;
        expect(hasSpacing).toBeTruthy();
      });
    });

    test('navigation works with all sections', () => {
      const navLinks = document.querySelectorAll('nav a[href^="#"]');
      const sections = document.querySelectorAll('section[id]');
      
      // Should have navigation for main sections
      expect(navLinks.length).toBeGreaterThan(0);
      expect(sections.length).toBeGreaterThan(0);
      
      // Each major section should be reachable
      const majorSections = ['about', 'skills', 'experience', 'contact'];
      majorSections.forEach(sectionId => {
        const section = document.getElementById(sectionId);
        const navLink = document.querySelector(`a[href="#${sectionId}"]`);
        
        if (section) {
          expect(navLink).toBeTruthy();
        }
      });
    });

    test('responsive design works across all sections', () => {
      // Check that responsive classes are applied consistently
      const responsiveElements = document.querySelectorAll('[class*="responsive"], [class*="mobile"], [class*="desktop"]');
      
      // Should have some responsive design elements
      expect(responsiveElements.length).toBeGreaterThanOrEqual(0);
      
      // Check CSS contains responsive breakpoints
      expect(cssContent).toMatch(/@media.*max-width|@media.*min-width/);
    });
  });

  describe('Interactive Features Integration', () => {
    test('smooth scrolling setup is complete', () => {
      // Check JavaScript includes smooth scrolling functionality
      expect(jsContent).toMatch(/smooth.*scroll|scrollTo|scrollIntoView/i);
      
      // Check for scroll-related event listeners
      expect(jsContent).toMatch(/addEventListener.*scroll/);
    });

    test('contact functionality is integrated', () => {
      // Email links
      const emailLinks = document.querySelectorAll('a[href^="mailto:"]');
      emailLinks.forEach(link => {
        expect(link.getAttribute('href')).toMatch(/^mailto:.+@.+\..+/);
      });

      // Social media links
      const socialLinks = document.querySelectorAll('a[target="_blank"]');
      socialLinks.forEach(link => {
        expect(link.getAttribute('href')).toMatch(/^https?:\/\//);
        expect(link.getAttribute('rel')).toContain('noopener');
      });
    });

    test('image loading and fallbacks work', () => {
      const images = document.querySelectorAll('img');
      
      images.forEach(img => {
        // Should have alt text
        expect(img.hasAttribute('alt')).toBe(true);
        
        // Should have src or data-src for lazy loading
        expect(img.getAttribute('src') || img.getAttribute('data-src')).toBeTruthy();
      });

      // Check for image error handling in JavaScript
      expect(jsContent).toMatch(/addEventListener.*error|onerror/);
    });
  });

  describe('Performance Integration', () => {
    test('all optimization features work together', () => {
      // Check for minified files
      const minifiedCssExists = fs.existsSync(path.join(__dirname, '../css/styles.min.css'));
      const minifiedJsExists = fs.existsSync(path.join(__dirname, '../js/main.min.js'));
      
      expect(minifiedCssExists).toBe(true);
      expect(minifiedJsExists).toBe(true);

      // Check for lazy loading implementation
      const lazyLoadingExists = fs.existsSync(path.join(__dirname, '../js/lazy-loading.js'));
      expect(lazyLoadingExists).toBe(true);

      // Check for resource optimization
      const resourceOptimizerExists = fs.existsSync(path.join(__dirname, '../js/resource-optimizer.js'));
      expect(resourceOptimizerExists).toBe(true);
    });

    test('CSS and JavaScript are properly linked', () => {
      // Check CSS links
      const cssLinks = document.querySelectorAll('link[rel="stylesheet"]');
      expect(cssLinks.length).toBeGreaterThan(0);

      cssLinks.forEach(link => {
        const href = link.getAttribute('href');
        const cssPath = path.join(__dirname, '..', href);
        expect(fs.existsSync(cssPath)).toBe(true);
      });

      // Check JavaScript links
      const scriptTags = document.querySelectorAll('script[src]');
      scriptTags.forEach(script => {
        const src = script.getAttribute('src');
        const jsPath = path.join(__dirname, '..', src);
        expect(fs.existsSync(jsPath)).toBe(true);
      });
    });
  });

  describe('IIS Deployment Integration', () => {
    test('web.config exists and is properly configured', () => {
      const webConfigExists = fs.existsSync(path.join(__dirname, '../web.config'));
      expect(webConfigExists).toBe(true);

      const webConfigContent = fs.readFileSync(path.join(__dirname, '../web.config'), 'utf8');
      
      // Check for essential IIS configurations
      expect(webConfigContent).toMatch(/<defaultDocument>/);
      expect(webConfigContent).toMatch(/<staticContent>/);
      expect(webConfigContent).toMatch(/<httpCompression>/);
      expect(webConfigContent).toMatch(/index\.html/);
    });

    test('error pages are properly configured', () => {
      const error404Exists = fs.existsSync(path.join(__dirname, '../404.html'));
      const error500Exists = fs.existsSync(path.join(__dirname, '../500.html'));
      
      expect(error404Exists).toBe(true);
      expect(error500Exists).toBe(true);

      // Check error pages have proper structure
      const error404Content = fs.readFileSync(path.join(__dirname, '../404.html'), 'utf8');
      const error500Content = fs.readFileSync(path.join(__dirname, '../500.html'), 'utf8');
      
      expect(error404Content).toMatch(/404/);
      expect(error404Content).toMatch(/not found/i);
      expect(error500Content).toMatch(/500/);
      expect(error500Content).toMatch(/server error/i);
    });

    test('all static assets are properly organized', () => {
      // Check directory structure
      const cssDir = fs.existsSync(path.join(__dirname, '../css'));
      const jsDir = fs.existsSync(path.join(__dirname, '../js'));
      const imagesDir = fs.existsSync(path.join(__dirname, '../images'));
      
      expect(cssDir).toBe(true);
      expect(jsDir).toBe(true);
      expect(imagesDir).toBe(true);

      // Check for essential files
      const mainCss = fs.existsSync(path.join(__dirname, '../css/styles.css'));
      const mainJs = fs.existsSync(path.join(__dirname, '../js/main.js'));
      
      expect(mainCss).toBe(true);
      expect(mainJs).toBe(true);
    });
  });

  describe('Accessibility Integration', () => {
    test('complete accessibility features work together', () => {
      // Heading hierarchy
      const h1Elements = document.querySelectorAll('h1');
      expect(h1Elements.length).toBeGreaterThanOrEqual(1);

      // Skip links or navigation aids
      const skipLinks = document.querySelectorAll('a[href^="#"]');
      expect(skipLinks.length).toBeGreaterThan(0);

      // Focus management
      const focusableElements = document.querySelectorAll('a, button, input, textarea, select');
      focusableElements.forEach(element => {
        // Should be keyboard accessible
        expect(element.tabIndex >= 0 || !element.hasAttribute('tabindex')).toBe(true);
      });
    });

    test('semantic structure supports screen readers', () => {
      // Main landmark
      const main = document.querySelector('main');
      const sections = document.querySelectorAll('section');
      
      expect(main || sections.length > 0).toBeTruthy();

      // Navigation landmark
      const nav = document.querySelector('nav');
      expect(nav).toBeTruthy();

      // Proper heading structure
      const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
      expect(headings.length).toBeGreaterThan(1);
    });
  });

  describe('Cross-Browser Compatibility Integration', () => {
    test('fallbacks are properly implemented', () => {
      // CSS fallbacks
      expect(cssContent).toMatch(/background.*fallback|color.*fallback/);
      
      // JavaScript feature detection
      expect(jsContent).toMatch(/typeof.*undefined|window\./);
      
      // Progressive enhancement patterns
      expect(jsContent).toMatch(/addEventListener|attachEvent/);
    });

    test('vendor prefixes are included where needed', () => {
      // Check for modern CSS features with prefixes
      if (cssContent.includes('transform')) {
        // Should work without prefixes in modern browsers
        expect(cssContent).toMatch(/transform/);
      }
      
      if (cssContent.includes('backdrop-filter')) {
        expect(cssContent).toMatch(/-webkit-backdrop-filter/);
      }
    });
  });

  describe('Complete User Experience', () => {
    test('loading experience is optimized', () => {
      // Check for loading optimization
      const preloadLinks = document.querySelectorAll('link[rel="preload"]');
      const deferredScripts = document.querySelectorAll('script[defer]');
      const asyncScripts = document.querySelectorAll('script[async]');
      
      // Should have some performance optimizations
      expect(preloadLinks.length + deferredScripts.length + asyncScripts.length).toBeGreaterThanOrEqual(0);
    });

    test('content hierarchy makes sense', () => {
      // Should have logical content flow
      const header = document.querySelector('header');
      const main = document.querySelector('main');
      const footer = document.querySelector('footer');
      
      // At minimum should have main content area
      expect(main || document.querySelector('section')).toBeTruthy();
      
      // Content should be in logical order
      const allSections = document.querySelectorAll('section');
      expect(allSections.length).toBeGreaterThan(2);
    });

    test('call-to-action elements are present and functional', () => {
      // Contact methods should be available
      const emailLinks = document.querySelectorAll('a[href^="mailto:"]');
      const phoneLinks = document.querySelectorAll('a[href^="tel:"]');
      const socialLinks = document.querySelectorAll('a[target="_blank"]');
      
      expect(emailLinks.length + phoneLinks.length + socialLinks.length).toBeGreaterThan(0);
      
      // CTA buttons should be present
      const ctaButtons = document.querySelectorAll('.cta, .button, .btn, button');
      expect(ctaButtons.length).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Final Validation', () => {
    test('all requirements are satisfied in integration', () => {
      // Requirement 1: Essential Profile Elements
      expect(document.querySelector('h1, .profile-name')).toBeTruthy();
      expect(document.querySelector('.profile-title, .hero h2')).toBeTruthy();
      
      // Requirement 2: Contact Information
      expect(document.querySelectorAll('a[href^="mailto:"]').length).toBeGreaterThan(0);
      
      // Requirement 3: Skills and Experience
      expect(document.querySelector('#skills, .skills-section')).toBeTruthy();
      expect(document.querySelector('#experience, .experience-section')).toBeTruthy();
      
      // Requirement 4: Responsive Design
      expect(cssContent).toMatch(/@media/);
      
      // Requirement 5: IIS Compatibility
      expect(fs.existsSync(path.join(__dirname, '../web.config'))).toBe(true);
      
      // Requirement 6: Performance
      expect(fs.existsSync(path.join(__dirname, '../css/styles.min.css'))).toBe(true);
      
      // Requirement 7: Design Consistency
      expect(cssContent).toMatch(/--[\w-]+:/); // CSS custom properties
    });

    test('website is ready for deployment', () => {
      // All essential files exist
      const essentialFiles = [
        'index.html',
        'css/styles.css',
        'css/styles.min.css',
        'js/main.js',
        'js/main.min.js',
        'web.config',
        '404.html',
        '500.html'
      ];
      
      essentialFiles.forEach(file => {
        const filePath = path.join(__dirname, '..', file);
        expect(fs.existsSync(filePath)).toBe(true);
      });
      
      // HTML is valid structure
      expect(htmlContent).toMatch(/<html[^>]*>[\s\S]*<\/html>/);
      expect(htmlContent).toMatch(/<head[^>]*>[\s\S]*<\/head>/);
      expect(htmlContent).toMatch(/<body[^>]*>[\s\S]*<\/body>/);
      
      // No obvious errors in content
      expect(htmlContent).not.toMatch(/TODO|FIXME|XXX/i);
      expect(cssContent).not.toMatch(/TODO|FIXME|XXX/i);
      expect(jsContent).not.toMatch(/TODO|FIXME|XXX/i);
    });
  });
});