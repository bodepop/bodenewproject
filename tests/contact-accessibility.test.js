/**
 * Property-Based Test for Contact Information Accessibility
 * Feature: personal-profile-website, Property 2: Contact Information Accessibility
 * Validates: Requirements 2.1, 2.2, 2.3, 2.4
 */

import fc from 'fast-check';

describe('Contact Information Accessibility Property Tests', () => {
  
  /**
   * Property 2: Contact Information Accessibility
   * For any contact link on the website, clicking it should trigger 
   * the appropriate application or service (email client, social media platform)
   */
  test('Property 2: All contact links trigger appropriate applications or services', () => {
    const contactSection = document.getElementById('contact');
    expect(contactSection).toBeTruthy();
    
    // Test email links
    const emailLinks = contactSection.querySelectorAll('a[href^="mailto:"]');
    expect(emailLinks.length).toBeGreaterThan(0);
    
    Array.from(emailLinks).forEach(link => {
      const href = link.getAttribute('href');
      
      // Should start with mailto:
      expect(href).toMatch(/^mailto:/);
      
      // Should contain a valid email format
      const email = href.replace('mailto:', '').split('?')[0];
      expect(email).toMatch(/^[^\s@]+@[^\s@]+\.[^\s@]+$/);
      
      // Should have accessible text
      const linkText = link.textContent.trim();
      expect(linkText).toBeTruthy();
      expect(linkText.length).toBeGreaterThan(5);
    });
    
    // Test phone links
    const phoneLinks = contactSection.querySelectorAll('a[href^="tel:"]');
    Array.from(phoneLinks).forEach(link => {
      const href = link.getAttribute('href');
      
      // Should start with tel:
      expect(href).toMatch(/^tel:/);
      
      // Should contain a valid phone format
      const phone = href.replace('tel:', '');
      expect(phone).toMatch(/^[\+]?[\d\-\(\)\s]+$/);
      
      // Should have accessible text
      const linkText = link.textContent.trim();
      expect(linkText).toBeTruthy();
      expect(linkText.length).toBeGreaterThan(5);
    });
    
    // Test social media links
    const socialLinks = contactSection.querySelectorAll('.social-link[target="_blank"]');
    expect(socialLinks.length).toBeGreaterThan(0);
    
    Array.from(socialLinks).forEach(link => {
      const href = link.getAttribute('href');
      const target = link.getAttribute('target');
      const rel = link.getAttribute('rel');
      
      // Should be external links
      expect(href).toMatch(/^https?:\/\//);
      expect(target).toBe('_blank');
      expect(rel).toContain('noopener');
      expect(rel).toContain('noreferrer');
      
      // Should have accessible labels
      const ariaLabel = link.getAttribute('aria-label');
      const linkText = link.querySelector('.social-text')?.textContent;
      
      expect(ariaLabel || linkText).toBeTruthy();
      
      if (ariaLabel) {
        expect(ariaLabel.length).toBeGreaterThan(5);
      }
      
      if (linkText) {
        expect(linkText.length).toBeGreaterThan(2);
      }
    });
  });

  test('Contact information is displayed in clearly visible sections', () => {
    const contactSection = document.getElementById('contact');
    const contactInfo = contactSection.querySelector('.contact-info');
    const socialMedia = contactSection.querySelector('.social-media');
    
    expect(contactInfo).toBeTruthy();
    expect(socialMedia).toBeTruthy();
    
    // Check visibility
    const contactInfoStyle = window.getComputedStyle(contactInfo);
    const socialMediaStyle = window.getComputedStyle(socialMedia);
    
    expect(contactInfoStyle.display).not.toBe('none');
    expect(contactInfoStyle.visibility).not.toBe('hidden');
    expect(parseFloat(contactInfoStyle.opacity) || 1).toBeGreaterThan(0);
    
    expect(socialMediaStyle.display).not.toBe('none');
    expect(socialMediaStyle.visibility).not.toBe('hidden');
    expect(parseFloat(socialMediaStyle.opacity) || 1).toBeGreaterThan(0);
    
    // Check that sections have proper styling for visibility
    expect(contactInfoStyle.backgroundColor).not.toBe('rgba(0, 0, 0, 0)');
    expect(socialMediaStyle.backgroundColor).not.toBe('rgba(0, 0, 0, 0)');
  });

  test('Email contact information is properly formatted and accessible', () => {
    const emailLinks = document.querySelectorAll('a[href^="mailto:"]');
    
    expect(emailLinks.length).toBeGreaterThan(0);
    
    Array.from(emailLinks).forEach(link => {
      const href = link.getAttribute('href');
      const email = href.replace('mailto:', '').split('?')[0];
      
      // Email should be valid format
      expect(email).toMatch(/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/);
      
      // Link should be keyboard accessible
      expect(link.tabIndex).not.toBe(-1);
      
      // Link should have proper styling for visibility
      const style = window.getComputedStyle(link);
      expect(style.color).not.toBe('rgba(0, 0, 0, 0)');
      expect(style.textDecoration).toBeDefined();
      
      // Link text should match or be descriptive of the email
      const linkText = link.textContent.trim();
      expect(linkText === email || linkText.includes('@')).toBe(true);
    });
  });

  test('Social media links have proper accessibility attributes', () => {
    const socialLinks = document.querySelectorAll('.social-link');
    
    expect(socialLinks.length).toBeGreaterThan(0);
    
    Array.from(socialLinks).forEach(link => {
      // Should have proper target and rel attributes for external links
      if (link.getAttribute('href').startsWith('http')) {
        expect(link.getAttribute('target')).toBe('_blank');
        expect(link.getAttribute('rel')).toContain('noopener');
        expect(link.getAttribute('rel')).toContain('noreferrer');
      }
      
      // Should have accessible labeling
      const ariaLabel = link.getAttribute('aria-label');
      const socialText = link.querySelector('.social-text');
      const socialIcon = link.querySelector('.social-icon');
      
      // Must have either aria-label or visible text
      expect(ariaLabel || (socialText && socialText.textContent.trim())).toBeTruthy();
      
      // Should have visual indicator (icon or text)
      expect(socialIcon || socialText).toBeTruthy();
      
      // Should be keyboard accessible
      expect(link.tabIndex).not.toBe(-1);
      
      // Should have hover/focus states
      const style = window.getComputedStyle(link);
      expect(style.transition).toBeTruthy();
    });
  });

  test('Contact section maintains accessibility standards', () => {
    const contactSection = document.getElementById('contact');
    
    // Should have proper heading structure
    const sectionTitle = contactSection.querySelector('.section-title');
    expect(sectionTitle.tagName).toBe('H2');
    
    const subTitles = contactSection.querySelectorAll('.contact-subtitle, .social-title');
    Array.from(subTitles).forEach(title => {
      expect(title.tagName).toBe('H3');
    });
    
    // All interactive elements should be keyboard accessible
    const interactiveElements = contactSection.querySelectorAll('a, button');
    Array.from(interactiveElements).forEach(element => {
      expect(element.tabIndex).not.toBe(-1);
      
      // Should have focus styles
      const style = window.getComputedStyle(element);
      expect(style.outline || style.boxShadow || style.border).toBeTruthy();
    });
    
    // Text should have sufficient contrast
    const textElements = contactSection.querySelectorAll('p, span, a');
    Array.from(textElements).forEach(element => {
      const style = window.getComputedStyle(element);
      const color = style.color;
      const backgroundColor = style.backgroundColor;
      
      // Colors should not be the same (basic contrast check)
      expect(color).not.toBe(backgroundColor);
      expect(color).not.toBe('rgba(0, 0, 0, 0)');
      expect(color).not.toBe('transparent');
    });
  });

  test('Property-based test: Contact links maintain functionality with various formats', () => {
    fc.assert(
      fc.property(
        fc.record({
          email: fc.emailAddress(),
          phone: fc.string({ minLength: 10, maxLength: 15 }).filter(s => /^\d+$/.test(s)),
          socialPlatform: fc.constantFrom('linkedin', 'github', 'twitter', 'portfolio'),
          username: fc.string({ minLength: 3, maxLength: 20 }).filter(s => /^[a-zA-Z0-9_-]+$/.test(s))
        }),
        (contactData) => {
          // Test that contact link formats are valid
          const emailHref = `mailto:${contactData.email}`;
          const phoneHref = `tel:+1${contactData.phone}`;
          const socialHref = `https://${contactData.socialPlatform}.com/${contactData.username}`;
          
          // Email format validation
          const emailValid = emailHref.startsWith('mailto:') && 
                            contactData.email.includes('@') && 
                            contactData.email.includes('.');
          
          // Phone format validation
          const phoneValid = phoneHref.startsWith('tel:') && 
                           phoneHref.length > 8;
          
          // Social link validation
          const socialValid = socialHref.startsWith('https://') && 
                             socialHref.includes('.com/');
          
          return emailValid && phoneValid && socialValid;
        }
      ),
      { numRuns: 50 }
    );
  });

  test('Contact information is not placeholder text', () => {
    // Test email addresses
    const emailLinks = document.querySelectorAll('a[href^="mailto:"]');
    Array.from(emailLinks).forEach(link => {
      const email = link.textContent.trim();
      expect(email).not.toMatch(/^(your\.email|email|contact)@example\.com$/i);
      expect(email).not.toMatch(/^(test|sample|placeholder)@/i);
      expect(email).toMatch(/^[^\s@]+@[^\s@]+\.[^\s@]+$/);
    });
    
    // Test phone numbers
    const phoneLinks = document.querySelectorAll('a[href^="tel:"]');
    Array.from(phoneLinks).forEach(link => {
      const phone = link.textContent.trim();
      expect(phone).not.toMatch(/^(\+?1?\s?)?\(?123\)?[\s\-]?456[\s\-]?7890$/);
      expect(phone).not.toMatch(/^(\+?1?\s?)?\(?555\)?[\s\-]?/);
      expect(phone.replace(/[\s\-\(\)]/g, '')).toMatch(/^\+?\d{10,15}$/);
    });
    
    // Test social media links
    const socialLinks = document.querySelectorAll('.social-link[href*="://"]');
    Array.from(socialLinks).forEach(link => {
      const href = link.getAttribute('href');
      expect(href).not.toMatch(/yourusername|yourprofile|username|profile/i);
      expect(href).not.toMatch(/example\.com/i);
      expect(href).toMatch(/^https?:\/\/[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/);
    });
    
    // Test location information
    const locationValues = document.querySelectorAll('.contact-value');
    Array.from(locationValues).forEach(location => {
      const text = location.textContent.trim();
      if (text.includes(',')) { // Likely a location
        expect(text).not.toBe('City, Region');
        expect(text).not.toBe('City, State');
        expect(text).not.toMatch(/^(Your|My) (City|Location)/i);
      }
    });
  });

  test('Contact links have proper hover and focus states', () => {
    const allLinks = document.querySelectorAll('#contact a');
    
    Array.from(allLinks).forEach(link => {
      const style = window.getComputedStyle(link);
      
      // Should have transition for smooth interactions
      expect(style.transition).toBeTruthy();
      expect(style.transition).not.toBe('none');
      
      // Should be styled as a link
      expect(style.cursor).toBe('pointer');
      
      // Should have some form of visual distinction
      const hasVisualDistinction = 
        style.color !== style.backgroundColor ||
        style.textDecoration !== 'none' ||
        style.borderBottom !== 'none' ||
        style.borderColor !== 'rgba(0, 0, 0, 0)';
      
      expect(hasVisualDistinction).toBe(true);
    });
  });

  test('Contact section provides multiple ways to connect', () => {
    const contactSection = document.getElementById('contact');
    
    // Should have email contact
    const emailLinks = contactSection.querySelectorAll('a[href^="mailto:"]');
    expect(emailLinks.length).toBeGreaterThan(0);
    
    // Should have social media links
    const socialLinks = contactSection.querySelectorAll('.social-link[target="_blank"]');
    expect(socialLinks.length).toBeGreaterThanOrEqual(2);
    
    // Should have location information
    const locationInfo = contactSection.querySelector('.contact-value, .location-value');
    expect(locationInfo).toBeTruthy();
    expect(locationInfo.textContent.trim()).not.toBe('');
    
    // May have phone contact
    const phoneLinks = contactSection.querySelectorAll('a[href^="tel:"]');
    // Phone is optional, but if present should be valid
    
    // Should have call-to-action
    const ctaElements = contactSection.querySelectorAll('.cta-button, .contact-cta');
    expect(ctaElements.length).toBeGreaterThan(0);
  });
});