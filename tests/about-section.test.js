/**
 * Unit Tests for About Section Content
 * Validates: Requirements 1.3, 1.5
 */

describe('About Section Content Tests', () => {
  
  test('About section exists and is properly structured', () => {
    const aboutSection = document.getElementById('about');
    expect(aboutSection).toBeTruthy();
    expect(aboutSection.classList.contains('about-section')).toBe(true);
    
    const sectionTitle = aboutSection.querySelector('.section-title');
    expect(sectionTitle).toBeTruthy();
    expect(sectionTitle.textContent.trim()).toBe('About Me');
  });

  test('Biography content is present and substantial', () => {
    const bioElements = document.querySelectorAll('.bio');
    
    expect(bioElements.length).toBeGreaterThanOrEqual(2);
    
    Array.from(bioElements).forEach((bio, index) => {
      const bioText = bio.textContent.trim();
      
      // Each bio paragraph should be substantial
      expect(bioText.length).toBeGreaterThan(50);
      expect(bioText.split(' ').length).toBeGreaterThan(15);
      
      // Should not be placeholder text
      expect(bioText).not.toMatch(/^(Professional biography paragraph|This should contain)/i);
      expect(bioText).not.toMatch(/lorem ipsum/i);
      
      // First bio should be more prominent
      if (index === 0) {
        const style = window.getComputedStyle(bio);
        const fontSize = parseFloat(style.fontSize);
        expect(fontSize).toBeGreaterThan(16); // Should be larger than base font
      }
    });
  });

  test('Location information is properly displayed', () => {
    const locationValue = document.querySelector('.location-value');
    const locationLabel = document.querySelector('.location-label');
    
    expect(locationValue).toBeTruthy();
    expect(locationLabel).toBeTruthy();
    
    const locationText = locationValue.textContent.trim();
    expect(locationText).not.toBe('');
    expect(locationText).not.toBe('City, Region');
    expect(locationText.length).toBeGreaterThan(5);
    
    // Should follow City, State/Region format
    expect(locationText).toMatch(/^[A-Za-z\s]+,\s*[A-Za-z\s]+$/);
    
    expect(locationLabel.textContent.trim()).toBe('Location:');
  });

  test('Achievements section is present and well-formatted', () => {
    const achievementsHighlight = document.querySelector('.achievements-highlight');
    const achievementsTitle = document.querySelector('.achievements-title');
    const achievementsList = document.querySelector('.achievements-list');
    
    expect(achievementsHighlight).toBeTruthy();
    expect(achievementsTitle).toBeTruthy();
    expect(achievementsList).toBeTruthy();
    
    expect(achievementsTitle.textContent.trim()).toBe('Key Highlights');
    
    const achievementItems = achievementsList.querySelectorAll('li');
    expect(achievementItems.length).toBeGreaterThanOrEqual(3);
    
    Array.from(achievementItems).forEach(item => {
      const itemText = item.textContent.trim();
      expect(itemText.length).toBeGreaterThan(20);
      expect(itemText).not.toMatch(/^(Achievement|Key achievement)/i);
    });
  });

  test('Additional info section (availability, languages) is present', () => {
    const availability = document.querySelector('.availability');
    const languages = document.querySelector('.languages');
    
    if (availability) {
      const availabilityLabel = availability.querySelector('.availability-label');
      const availabilityValue = availability.querySelector('.availability-value');
      
      expect(availabilityLabel).toBeTruthy();
      expect(availabilityValue).toBeTruthy();
      expect(availabilityLabel.textContent.trim()).toBe('Availability:');
      expect(availabilityValue.textContent.trim()).not.toBe('');
    }
    
    if (languages) {
      const languagesLabel = languages.querySelector('.languages-label');
      const languagesValue = languages.querySelector('.languages-value');
      
      expect(languagesLabel).toBeTruthy();
      expect(languagesValue).toBeTruthy();
      expect(languagesLabel.textContent.trim()).toBe('Languages:');
      expect(languagesValue.textContent.trim()).not.toBe('');
    }
  });

  test('About section has proper styling and layout', () => {
    const aboutContent = document.querySelector('.about-content');
    const bioContent = document.querySelector('.bio-content');
    const locationInfo = document.querySelector('.location-info');
    
    expect(aboutContent).toBeTruthy();
    expect(bioContent).toBeTruthy();
    expect(locationInfo).toBeTruthy();
    
    // Check grid layout on desktop
    const aboutStyle = window.getComputedStyle(aboutContent);
    expect(aboutStyle.display).toBe('grid');
    
    // Check that location info has proper styling
    const locationStyle = window.getComputedStyle(locationInfo);
    expect(locationStyle.backgroundColor).not.toBe('rgba(0, 0, 0, 0)');
    expect(locationStyle.padding).not.toBe('0px');
    expect(locationStyle.borderRadius).not.toBe('0px');
  });

  test('Biography text has proper typography and readability', () => {
    const bioElements = document.querySelectorAll('.bio');
    
    Array.from(bioElements).forEach(bio => {
      const style = window.getComputedStyle(bio);
      const fontSize = parseFloat(style.fontSize);
      const lineHeight = parseFloat(style.lineHeight) || fontSize * 1.5;
      
      // Font size should be readable
      expect(fontSize).toBeGreaterThanOrEqual(14);
      
      // Line height should provide good readability
      expect(lineHeight).toBeGreaterThan(fontSize * 1.2);
      
      // Should have proper margins for spacing
      const marginBottom = parseFloat(style.marginBottom);
      expect(marginBottom).toBeGreaterThan(0);
      
      // Text should be visible
      expect(style.display).not.toBe('none');
      expect(style.visibility).not.toBe('hidden');
      expect(parseFloat(style.opacity) || 1).toBeGreaterThan(0);
    });
  });

  test('Achievements list has proper formatting and icons', () => {
    const achievementItems = document.querySelectorAll('.achievements-list li');
    
    Array.from(achievementItems).forEach(item => {
      const style = window.getComputedStyle(item);
      const beforeStyle = window.getComputedStyle(item, '::before');
      
      // Should have left padding for icon
      const paddingLeft = parseFloat(style.paddingLeft);
      expect(paddingLeft).toBeGreaterThan(16);
      
      // Should have proper positioning
      expect(style.position).toBe('relative');
      
      // Text should be readable
      const fontSize = parseFloat(style.fontSize);
      expect(fontSize).toBeGreaterThanOrEqual(14);
    });
  });

  test('Location info section has proper interactive styling', () => {
    const locationInfo = document.querySelector('.location-info');
    
    if (locationInfo) {
      const style = window.getComputedStyle(locationInfo);
      
      // Should have background and padding
      expect(style.backgroundColor).not.toBe('rgba(0, 0, 0, 0)');
      expect(parseFloat(style.padding)).toBeGreaterThan(16);
      
      // Should have border radius
      expect(parseFloat(style.borderRadius)).toBeGreaterThan(0);
      
      // Should have box shadow
      expect(style.boxShadow).not.toBe('none');
    }
  });

  test('About section is accessible', () => {
    const aboutSection = document.getElementById('about');
    const sectionTitle = aboutSection.querySelector('.section-title');
    
    // Section should have proper heading structure
    expect(sectionTitle.tagName).toBe('H2');
    
    // All text should be readable (not empty)
    const textElements = aboutSection.querySelectorAll('p, span, li');
    Array.from(textElements).forEach(element => {
      if (element.textContent) {
        expect(element.textContent.trim()).not.toBe('');
      }
    });
    
    // Labels should be properly associated with values
    const labels = aboutSection.querySelectorAll('[class$="-label"]');
    const values = aboutSection.querySelectorAll('[class$="-value"]');
    
    expect(labels.length).toBe(values.length);
  });

  test('About section content is not placeholder text', () => {
    const bioElements = document.querySelectorAll('.bio');
    const locationValue = document.querySelector('.location-value');
    const achievementItems = document.querySelectorAll('.achievements-list li');
    
    // Bio should not be placeholder
    Array.from(bioElements).forEach(bio => {
      const text = bio.textContent.trim();
      expect(text).not.toMatch(/^(Professional biography|This should|Lorem ipsum)/i);
      expect(text).not.toMatch(/placeholder|example|sample/i);
    });
    
    // Location should not be placeholder
    if (locationValue) {
      const locationText = locationValue.textContent.trim();
      expect(locationText).not.toBe('City, Region');
      expect(locationText).not.toMatch(/^(City|Location|Place)/i);
    }
    
    // Achievements should not be placeholder
    Array.from(achievementItems).forEach(item => {
      const text = item.textContent.trim();
      expect(text).not.toMatch(/^(Key achievement|Achievement|Sample)/i);
    });
  });
});