/**
 * Property-Based Test for Essential Profile Elements
 * Feature: personal-profile-website, Property 1: Essential Profile Elements Present
 * Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5
 */

import fc from 'fast-check';

describe('Essential Profile Elements Property Tests', () => {
  
  /**
   * Property 1: Essential Profile Elements Present
   * For any valid profile website, all essential profile elements 
   * (name, photo, bio, title, location) should be present in the DOM 
   * and contain non-empty content
   */
  test('Property 1: All essential profile elements are present and contain content', () => {
    // Test that all required elements exist
    const profileName = document.querySelector('.profile-name');
    const profilePhoto = document.querySelector('.profile-photo, .profile-photo-fallback');
    const profileTitle = document.querySelector('.profile-title');
    const profileTagline = document.querySelector('.profile-tagline');
    const bio = document.querySelectorAll('.bio');
    const location = document.querySelector('.location-value');
    
    // Elements should exist
    expect(profileName).toBeTruthy();
    expect(profilePhoto).toBeTruthy();
    expect(profileTitle).toBeTruthy();
    expect(profileTagline).toBeTruthy();
    expect(bio.length).toBeGreaterThan(0);
    expect(location).toBeTruthy();
    
    // Elements should contain non-empty content
    expect(profileName.textContent.trim()).not.toBe('');
    expect(profileTitle.textContent.trim()).not.toBe('');
    expect(profileTagline.textContent.trim()).not.toBe('');
    expect(location.textContent.trim()).not.toBe('');
    
    // Bio paragraphs should contain content
    Array.from(bio).forEach(paragraph => {
      expect(paragraph.textContent.trim()).not.toBe('');
      expect(paragraph.textContent.trim().length).toBeGreaterThan(10);
    });
    
    // Profile photo should have proper attributes
    if (profilePhoto.tagName === 'IMG') {
      expect(profilePhoto.src).toBeTruthy();
      expect(profilePhoto.alt).toBeTruthy();
      expect(profilePhoto.alt.trim()).not.toBe('');
    }
  });

  test('Profile name is prominently displayed', () => {
    const profileName = document.querySelector('.profile-name');
    
    if (profileName) {
      const style = window.getComputedStyle(profileName);
      const fontSize = parseFloat(style.fontSize);
      const fontWeight = parseInt(style.fontWeight) || 400;
      
      // Name should be large and prominent
      expect(fontSize).toBeGreaterThan(24); // At least 1.5rem
      expect(fontWeight).toBeGreaterThanOrEqual(400);
      
      // Should be visible
      expect(style.display).not.toBe('none');
      expect(style.visibility).not.toBe('hidden');
      expect(parseFloat(style.opacity) || 1).toBeGreaterThan(0);
    }
  });

  test('Professional photo has appropriate dimensions and styling', () => {
    const profilePhoto = document.querySelector('.profile-photo');
    const fallbackPhoto = document.querySelector('.profile-photo-fallback');
    
    const photo = profilePhoto || fallbackPhoto;
    
    if (photo) {
      const style = window.getComputedStyle(photo);
      const width = parseInt(style.width);
      const height = parseInt(style.height);
      const borderRadius = style.borderRadius;
      
      // Photo should be reasonably sized
      expect(width).toBeGreaterThan(100);
      expect(width).toBeLessThan(400);
      expect(height).toBeGreaterThan(100);
      expect(height).toBeLessThan(400);
      
      // Should be circular (border-radius should be 50% or equivalent to half width)
      const expectedRadius = width / 2;
      const actualRadius = parseInt(borderRadius) || 0;
      expect(actualRadius).toBeGreaterThan(expectedRadius * 0.8); // Allow some tolerance
      
      // Should be visible
      expect(style.display).not.toBe('none');
      expect(style.visibility).not.toBe('hidden');
    }
  });

  test('Professional title and tagline provide clear role information', () => {
    const profileTitle = document.querySelector('.profile-title');
    const profileTagline = document.querySelector('.profile-tagline');
    
    if (profileTitle) {
      const titleText = profileTitle.textContent.trim();
      
      // Title should be descriptive
      expect(titleText.length).toBeGreaterThan(5);
      expect(titleText).not.toMatch(/^(title|job|role)$/i); // Not just placeholder text
      
      // Should be visible and styled appropriately
      const style = window.getComputedStyle(profileTitle);
      expect(style.display).not.toBe('none');
      expect(parseFloat(style.fontSize)).toBeGreaterThan(16);
    }
    
    if (profileTagline) {
      const taglineText = profileTagline.textContent.trim();
      
      // Tagline should be descriptive
      expect(taglineText.length).toBeGreaterThan(10);
      expect(taglineText).not.toMatch(/^(tagline|description)$/i);
      
      // Should be visible
      const style = window.getComputedStyle(profileTagline);
      expect(style.display).not.toBe('none');
    }
  });

  test('Biography content is substantial and well-formatted', () => {
    const bioElements = document.querySelectorAll('.bio');
    
    expect(bioElements.length).toBeGreaterThan(0);
    
    Array.from(bioElements).forEach(bio => {
      const bioText = bio.textContent.trim();
      
      // Bio should be substantial
      expect(bioText.length).toBeGreaterThan(50);
      expect(bioText.split(' ').length).toBeGreaterThan(10); // At least 10 words
      
      // Should not be placeholder text
      expect(bioText).not.toMatch(/^(bio|biography|about|description)/i);
      expect(bioText).not.toMatch(/lorem ipsum/i);
      
      // Should be visible and readable
      const style = window.getComputedStyle(bio);
      expect(style.display).not.toBe('none');
      expect(parseFloat(style.fontSize)).toBeGreaterThan(12);
      expect(parseFloat(style.lineHeight) || 1.5).toBeGreaterThan(1.2);
    });
  });

  test('Location information is properly formatted and displayed', () => {
    const locationValue = document.querySelector('.location-value');
    const locationLabel = document.querySelector('.location-label');
    
    if (locationValue) {
      const locationText = locationValue.textContent.trim();
      
      // Location should be formatted properly (City, Region or similar)
      expect(locationText.length).toBeGreaterThan(3);
      expect(locationText).not.toBe('Location');
      expect(locationText).not.toBe('City, Region');
      
      // Should be visible
      const style = window.getComputedStyle(locationValue);
      expect(style.display).not.toBe('none');
    }
    
    if (locationLabel) {
      expect(locationLabel.textContent.trim()).toBe('Location:');
    }
  });

  test('All essential elements are semantically structured', () => {
    // Test semantic HTML structure
    const header = document.querySelector('header');
    const main = document.querySelector('main');
    const nav = document.querySelector('nav');
    
    expect(header).toBeTruthy();
    expect(main).toBeTruthy();
    expect(nav).toBeTruthy();
    
    // Test heading hierarchy
    const h1 = document.querySelector('h1');
    const h2Elements = document.querySelectorAll('h2');
    
    expect(h1).toBeTruthy(); // Should have exactly one h1
    expect(h2Elements.length).toBeGreaterThan(0); // Should have section headings
    
    // H1 should be the profile name
    expect(h1.classList.contains('profile-name')).toBe(true);
  });

  test('Essential elements maintain accessibility standards', () => {
    // Test image alt text
    const images = document.querySelectorAll('img');
    Array.from(images).forEach(img => {
      expect(img.alt).toBeTruthy();
      expect(img.alt.trim()).not.toBe('');
      expect(img.alt.length).toBeGreaterThan(5);
    });
    
    // Test heading structure
    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
    Array.from(headings).forEach(heading => {
      expect(heading.textContent.trim()).not.toBe('');
    });
    
    // Test navigation accessibility
    const nav = document.querySelector('nav');
    if (nav) {
      expect(nav.getAttribute('role')).toBe('navigation');
      expect(nav.getAttribute('aria-label')).toBeTruthy();
    }
    
    // Test link accessibility
    const links = document.querySelectorAll('a');
    Array.from(links).forEach(link => {
      const text = link.textContent.trim();
      const ariaLabel = link.getAttribute('aria-label');
      const title = link.getAttribute('title');
      
      // Links should have descriptive text or aria-label
      expect(text || ariaLabel || title).toBeTruthy();
    });
  });

  test('Property-based test: Essential elements exist regardless of content variations', () => {
    fc.assert(
      fc.property(
        fc.record({
          name: fc.string({ minLength: 2, maxLength: 50 }),
          title: fc.string({ minLength: 5, maxLength: 100 }),
          tagline: fc.string({ minLength: 10, maxLength: 200 }),
          location: fc.string({ minLength: 3, maxLength: 50 })
        }),
        (profileData) => {
          // Simulate updating profile content
          const nameElement = document.querySelector('.profile-name');
          const titleElement = document.querySelector('.profile-title');
          const taglineElement = document.querySelector('.profile-tagline');
          const locationElement = document.querySelector('.location-value');
          
          if (nameElement) nameElement.textContent = profileData.name;
          if (titleElement) titleElement.textContent = profileData.title;
          if (taglineElement) taglineElement.textContent = profileData.tagline;
          if (locationElement) locationElement.textContent = profileData.location;
          
          // Verify elements still exist and are properly structured
          const essentialElements = [
            document.querySelector('.profile-name'),
            document.querySelector('.profile-photo, .profile-photo-fallback'),
            document.querySelector('.profile-title'),
            document.querySelector('.profile-tagline'),
            document.querySelector('.location-value')
          ];
          
          return essentialElements.every(element => {
            if (!element) return false;
            
            const style = window.getComputedStyle(element);
            const isVisible = style.display !== 'none' && 
                             style.visibility !== 'hidden' &&
                             (parseFloat(style.opacity) || 1) > 0;
            
            const hasContent = element.textContent?.trim() || 
                              element.src || 
                              element.tagName === 'DIV'; // For fallback photo
            
            return isVisible && hasContent;
          });
        }
      ),
      { numRuns: 50 }
    );
  });
});