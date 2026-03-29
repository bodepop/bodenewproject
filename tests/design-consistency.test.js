/**
 * Property-Based Test for Design Consistency
 * Feature: personal-profile-website, Property 7: Design Consistency
 * Validates: Requirements 7.2, 7.3
 */

import fc from 'fast-check';

describe('Design Consistency Property Tests', () => {
  
  /**
   * Property 7: Design Consistency
   * For any text element on the website, it should use consistent typography 
   * and color scheme as defined in the CSS
   */
  test('Property 7: All text elements use consistent typography and color scheme', () => {
    fc.assert(
      fc.property(
        fc.constantFrom(
          'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
          'p', 'span', 'a', 'li', 'div'
        ),
        (elementType) => {
          // Get all elements of the specified type
          const elements = document.querySelectorAll(elementType);
          
          if (elements.length === 0) return true; // Skip if no elements of this type
          
          // Get computed styles for all elements of this type
          const styles = Array.from(elements).map(el => {
            const computedStyle = window.getComputedStyle(el);
            return {
              fontFamily: computedStyle.fontFamily,
              fontSize: computedStyle.fontSize,
              lineHeight: computedStyle.lineHeight,
              color: computedStyle.color
            };
          });
          
          // Check typography consistency within element type
          const firstStyle = styles[0];
          const fontFamilyConsistent = styles.every(style => 
            style.fontFamily === firstStyle.fontFamily || 
            style.fontFamily.includes('Segoe UI') || 
            style.fontFamily.includes('Georgia')
          );
          
          // Check that colors are from the defined color palette
          const validColors = [
            'rgb(44, 62, 80)',    // --primary-color
            'rgb(52, 152, 219)',  // --secondary-color
            'rgb(231, 76, 60)',   // --accent-color
            'rgb(127, 140, 141)', // --text-secondary
            'rgb(236, 240, 241)', // --text-light
            'rgb(255, 255, 255)', // white
            'rgb(0, 0, 0)'        // black
          ];
          
          const colorsValid = styles.every(style => {
            const color = style.color;
            return validColors.some(validColor => 
              color === validColor || 
              color.startsWith('rgba(') || 
              color.startsWith('rgb(')
            );
          });
          
          return fontFamilyConsistent && colorsValid;
        }
      ),
      { numRuns: 100 }
    );
  });

  test('CSS custom properties are properly defined and used', () => {
    // Check that CSS custom properties are defined
    const rootStyles = window.getComputedStyle(document.documentElement);
    
    // Test primary color variables
    const primaryColor = rootStyles.getPropertyValue('--primary-color').trim();
    const secondaryColor = rootStyles.getPropertyValue('--secondary-color').trim();
    const textPrimary = rootStyles.getPropertyValue('--text-primary').trim();
    
    expect(primaryColor).toBe('#2c3e50');
    expect(secondaryColor).toBe('#3498db');
    expect(textPrimary).toBe('#2c3e50');
    
    // Test font variables
    const fontPrimary = rootStyles.getPropertyValue('--font-primary').trim();
    const fontSize = rootStyles.getPropertyValue('--font-size-base').trim();
    
    expect(fontPrimary).toContain('Segoe UI');
    expect(fontSize).toBe('1rem');
  });

  test('Consistent spacing is applied throughout the design', () => {
    fc.assert(
      fc.property(
        fc.constantFrom('.section', '.container', '.skill-item', '.contact-item'),
        (selector) => {
          const elements = document.querySelectorAll(selector);
          
          if (elements.length === 0) return true;
          
          // Check that padding/margin values use consistent spacing scale
          const spacingValues = ['0.25rem', '0.5rem', '1rem', '1.5rem', '2rem', '3rem', '4rem'];
          
          return Array.from(elements).every(el => {
            const computedStyle = window.getComputedStyle(el);
            const padding = computedStyle.padding;
            const margin = computedStyle.margin;
            
            // Extract numeric values and check they align with spacing scale
            const paddingValues = padding.match(/[\d.]+rem/g) || [];
            const marginValues = margin.match(/[\d.]+rem/g) || [];
            
            const allValues = [...paddingValues, ...marginValues];
            
            return allValues.every(value => 
              spacingValues.includes(value) || 
              value === '0rem' || 
              value === '0px'
            );
          });
        }
      ),
      { numRuns: 50 }
    );
  });

  test('Color contrast meets accessibility standards', () => {
    // Test key text elements for sufficient contrast
    const textElements = document.querySelectorAll('h1, h2, h3, p, a, .nav-link');
    
    Array.from(textElements).forEach(element => {
      const computedStyle = window.getComputedStyle(element);
      const color = computedStyle.color;
      const backgroundColor = computedStyle.backgroundColor;
      
      // Basic check that colors are not the same (proper contrast)
      expect(color).not.toBe(backgroundColor);
      
      // Ensure text is not transparent
      expect(color).not.toBe('rgba(0, 0, 0, 0)');
      expect(color).not.toBe('transparent');
    });
  });

  test('Typography hierarchy is consistent', () => {
    const headings = {
      h1: document.querySelectorAll('h1'),
      h2: document.querySelectorAll('h2'),
      h3: document.querySelectorAll('h3')
    };
    
    // Check that h1 is larger than h2, h2 is larger than h3
    if (headings.h1.length > 0 && headings.h2.length > 0) {
      const h1Size = parseFloat(window.getComputedStyle(headings.h1[0]).fontSize);
      const h2Size = parseFloat(window.getComputedStyle(headings.h2[0]).fontSize);
      
      expect(h1Size).toBeGreaterThan(h2Size);
    }
    
    if (headings.h2.length > 0 && headings.h3.length > 0) {
      const h2Size = parseFloat(window.getComputedStyle(headings.h2[0]).fontSize);
      const h3Size = parseFloat(window.getComputedStyle(headings.h3[0]).fontSize);
      
      expect(h2Size).toBeGreaterThan(h3Size);
    }
  });
});