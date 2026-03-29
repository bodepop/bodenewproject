/**
 * Property-Based Test for Responsive Layout Adaptation
 * Feature: personal-profile-website, Property 4: Responsive Layout Adaptation
 * Validates: Requirements 4.1, 4.2, 4.3, 4.4
 */

import fc from 'fast-check';

describe('Responsive Layout Adaptation Property Tests', () => {
  
  // Helper function to simulate viewport resize
  const setViewportSize = (width, height) => {
    // Mock window dimensions
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: width,
    });
    Object.defineProperty(window, 'innerHeight', {
      writable: true,
      configurable: true,
      value: height,
    });
    
    // Trigger resize event
    window.dispatchEvent(new Event('resize'));
  };

  /**
   * Property 4: Responsive Layout Adaptation
   * For any viewport size (mobile, tablet, desktop), the website layout 
   * should adapt appropriately while maintaining readability
   */
  test('Property 4: Layout adapts appropriately across all viewport sizes', () => {
    fc.assert(
      fc.property(
        fc.record({
          width: fc.integer({ min: 320, max: 1920 }),
          height: fc.integer({ min: 568, max: 1080 })
        }),
        ({ width, height }) => {
          setViewportSize(width, height);
          
          // Test key responsive elements
          const nav = document.querySelector('.nav');
          const hero = document.querySelector('.hero');
          const skillsContent = document.querySelector('.skills-content');
          const contactContent = document.querySelector('.contact-content');
          
          if (!nav || !hero || !skillsContent || !contactContent) {
            return true; // Skip if elements don't exist
          }
          
          // Check that elements are visible and have reasonable dimensions
          const navStyle = window.getComputedStyle(nav);
          const heroStyle = window.getComputedStyle(hero);
          const skillsStyle = window.getComputedStyle(skillsContent);
          const contactStyle = window.getComputedStyle(contactContent);
          
          // Navigation should always be visible
          const navVisible = navStyle.display !== 'none' && navStyle.visibility !== 'hidden';
          
          // Hero section should have reasonable height
          const heroHeight = parseInt(heroStyle.minHeight) || parseInt(heroStyle.height);
          const heroReasonable = heroHeight > 200 || heroStyle.minHeight === 'auto';
          
          // Grid layouts should adapt to viewport width
          const skillsColumns = skillsStyle.gridTemplateColumns;
          const contactColumns = contactStyle.gridTemplateColumns;
          
          // Mobile: should use single column or adapt appropriately
          if (width < 768) {
            const skillsMobile = skillsColumns.includes('1fr') || skillsColumns === 'none';
            const contactMobile = contactColumns.includes('1fr') || contactColumns === 'none';
            return navVisible && heroReasonable && skillsMobile && contactMobile;
          }
          
          // Tablet and Desktop: can use multiple columns
          return navVisible && heroReasonable;
        }
      ),
      { numRuns: 100 }
    );
  });

  test('Mobile layout (320px-767px) uses appropriate single-column layouts', () => {
    const mobileWidths = [320, 375, 414, 480, 600, 767];
    
    mobileWidths.forEach(width => {
      setViewportSize(width, 800);
      
      const skillsContent = document.querySelector('.skills-content');
      const contactContent = document.querySelector('.contact-content');
      
      if (skillsContent && contactContent) {
        const skillsStyle = window.getComputedStyle(skillsContent);
        const contactStyle = window.getComputedStyle(contactContent);
        
        // On mobile, layouts should be single column or adapt appropriately
        const skillsColumns = skillsStyle.gridTemplateColumns;
        const contactColumns = contactStyle.gridTemplateColumns;
        
        // Should not have complex multi-column layouts on mobile
        expect(skillsColumns).not.toContain('repeat(3');
        expect(contactColumns).not.toContain('repeat(3');
      }
    });
  });

  test('Tablet layout (768px-1023px) uses appropriate two-column layouts', () => {
    const tabletWidths = [768, 800, 900, 1000, 1023];
    
    tabletWidths.forEach(width => {
      setViewportSize(width, 800);
      
      const skillsContent = document.querySelector('.skills-content');
      const contactContent = document.querySelector('.contact-content');
      
      if (skillsContent && contactContent) {
        const skillsStyle = window.getComputedStyle(skillsContent);
        const contactStyle = window.getComputedStyle(contactContent);
        
        // On tablet, should support two-column layouts
        const skillsColumns = skillsStyle.gridTemplateColumns;
        const contactColumns = contactStyle.gridTemplateColumns;
        
        // Should be able to handle multiple columns
        const skillsMultiColumn = skillsColumns.includes('1fr 1fr') || 
                                 skillsColumns.includes('repeat(2') ||
                                 skillsColumns.includes('minmax');
        const contactMultiColumn = contactColumns.includes('1fr 1fr') || 
                                  contactColumns.includes('repeat(2') ||
                                  contactColumns.includes('minmax');
        
        expect(skillsMultiColumn || skillsColumns === 'none').toBe(true);
        expect(contactMultiColumn || contactColumns === 'none').toBe(true);
      }
    });
  });

  test('Desktop layout (1024px+) uses optimized multi-column layouts', () => {
    const desktopWidths = [1024, 1200, 1400, 1600, 1920];
    
    desktopWidths.forEach(width => {
      setViewportSize(width, 800);
      
      const container = document.querySelector('.container');
      const skillsContent = document.querySelector('.skills-content');
      
      if (container && skillsContent) {
        const containerStyle = window.getComputedStyle(container);
        const skillsStyle = window.getComputedStyle(skillsContent);
        
        // Container should have reasonable max-width
        const maxWidth = parseInt(containerStyle.maxWidth);
        expect(maxWidth).toBeGreaterThan(800);
        
        // Skills should support multi-column layout
        const skillsColumns = skillsStyle.gridTemplateColumns;
        const supportsMultiColumn = skillsColumns.includes('1fr') || 
                                   skillsColumns.includes('repeat') ||
                                   skillsColumns.includes('minmax');
        
        expect(supportsMultiColumn || skillsColumns === 'none').toBe(true);
      }
    });
  });

  test('Text remains readable across all viewport sizes', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 320, max: 1920 }),
        (width) => {
          setViewportSize(width, 800);
          
          // Test key text elements for readability
          const textElements = document.querySelectorAll('h1, h2, h3, p, .nav-link');
          
          return Array.from(textElements).every(element => {
            const style = window.getComputedStyle(element);
            const fontSize = parseFloat(style.fontSize);
            const lineHeight = parseFloat(style.lineHeight) || fontSize * 1.5;
            
            // Font size should be at least 14px for readability
            const readableSize = fontSize >= 14;
            
            // Line height should be reasonable (not too cramped)
            const readableLineHeight = lineHeight >= fontSize * 1.2;
            
            // Text should not be invisible
            const visible = style.display !== 'none' && 
                           style.visibility !== 'hidden' &&
                           style.opacity !== '0';
            
            return readableSize && readableLineHeight && visible;
          });
        }
      ),
      { numRuns: 50 }
    );
  });

  test('Navigation remains accessible across all viewport sizes', () => {
    const viewportSizes = [
      { width: 320, height: 568 },  // iPhone SE
      { width: 375, height: 667 },  // iPhone 8
      { width: 768, height: 1024 }, // iPad
      { width: 1024, height: 768 }, // Desktop
      { width: 1920, height: 1080 } // Large Desktop
    ];
    
    viewportSizes.forEach(({ width, height }) => {
      setViewportSize(width, height);
      
      const nav = document.querySelector('.nav');
      const navLinks = document.querySelectorAll('.nav-link');
      
      if (nav && navLinks.length > 0) {
        const navStyle = window.getComputedStyle(nav);
        
        // Navigation should be visible
        expect(navStyle.display).not.toBe('none');
        expect(navStyle.visibility).not.toBe('hidden');
        
        // Navigation links should be accessible
        Array.from(navLinks).forEach(link => {
          const linkStyle = window.getComputedStyle(link);
          const fontSize = parseFloat(linkStyle.fontSize);
          
          // Links should be large enough to tap/click
          expect(fontSize).toBeGreaterThanOrEqual(14);
          
          // Links should be visible
          expect(linkStyle.display).not.toBe('none');
          expect(linkStyle.visibility).not.toBe('hidden');
        });
      }
    });
  });

  test('Images scale appropriately across viewport sizes', () => {
    const profilePhoto = document.querySelector('.profile-photo');
    
    if (profilePhoto) {
      const viewportSizes = [320, 480, 768, 1024, 1200];
      
      viewportSizes.forEach(width => {
        setViewportSize(width, 800);
        
        const style = window.getComputedStyle(profilePhoto);
        const imageWidth = parseInt(style.width);
        const imageHeight = parseInt(style.height);
        
        // Image should maintain aspect ratio (square for profile photo)
        expect(Math.abs(imageWidth - imageHeight)).toBeLessThanOrEqual(2);
        
        // Image should be reasonable size (not too small or too large)
        expect(imageWidth).toBeGreaterThanOrEqual(100);
        expect(imageWidth).toBeLessThanOrEqual(300);
        
        // Image should not overflow viewport on mobile
        if (width < 768) {
          expect(imageWidth).toBeLessThanOrEqual(width * 0.8);
        }
      });
    }
  });

  test('Content sections maintain proper spacing across viewport sizes', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 320, max: 1920 }),
        (width) => {
          setViewportSize(width, 800);
          
          const sections = document.querySelectorAll('.section');
          
          return Array.from(sections).every(section => {
            const style = window.getComputedStyle(section);
            const paddingTop = parseInt(style.paddingTop);
            const paddingBottom = parseInt(style.paddingBottom);
            
            // Sections should have reasonable padding
            const reasonablePadding = paddingTop >= 16 && paddingBottom >= 16;
            
            // Sections should not have excessive padding on mobile
            if (width < 768) {
              const notExcessive = paddingTop <= 64 && paddingBottom <= 64;
              return reasonablePadding && notExcessive;
            }
            
            return reasonablePadding;
          });
        }
      ),
      { numRuns: 50 }
    );
  });
});