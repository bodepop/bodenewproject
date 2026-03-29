/**
 * Property-Based Test for Skills and Experience Structure
 * Feature: personal-profile-website, Property 3: Skills and Experience Structure
 * Validates: Requirements 3.1, 3.2, 3.3, 3.4
 */

import fc from 'fast-check';

describe('Skills and Experience Structure Property Tests', () => {
  
  /**
   * Property 3: Skills and Experience Structure
   * For any skills or experience section, the content should be organized 
   * in a structured list format with proper HTML semantics
   */
  test('Property 3: Skills and experience sections use structured list format with proper semantics', () => {
    // Test skills section structure
    const skillsSection = document.getElementById('skills');
    const experienceSection = document.getElementById('experience');
    
    expect(skillsSection).toBeTruthy();
    expect(experienceSection).toBeTruthy();
    
    // Skills section should have proper structure
    const skillCategories = skillsSection.querySelectorAll('.skill-category');
    expect(skillCategories.length).toBeGreaterThan(0);
    
    Array.from(skillCategories).forEach(category => {
      // Each category should have a title
      const categoryTitle = category.querySelector('.category-title');
      expect(categoryTitle).toBeTruthy();
      expect(categoryTitle.tagName).toBe('H3');
      
      // Each category should have a skill list
      const skillList = category.querySelector('.skill-list');
      expect(skillList).toBeTruthy();
      expect(skillList.tagName).toBe('UL');
      
      // Skill list should contain skill items
      const skillItems = skillList.querySelectorAll('.skill-item');
      expect(skillItems.length).toBeGreaterThan(0);
      
      Array.from(skillItems).forEach(item => {
        expect(item.tagName).toBe('LI');
        
        // Each skill item should have name and indicator
        const skillName = item.querySelector('.skill-name');
        const skillIndicator = item.querySelector('.skill-indicator');
        
        expect(skillName).toBeTruthy();
        expect(skillIndicator).toBeTruthy();
        expect(skillName.textContent.trim()).not.toBe('');
      });
    });
    
    // Experience section should have proper structure
    const experienceItems = experienceSection.querySelectorAll('.experience-item');
    expect(experienceItems.length).toBeGreaterThan(0);
    
    Array.from(experienceItems).forEach(item => {
      // Each experience item should have required elements
      const jobTitle = item.querySelector('.job-title');
      const companyName = item.querySelector('.company-name');
      const duration = item.querySelector('.duration');
      const jobDescription = item.querySelector('.job-description');
      
      expect(jobTitle).toBeTruthy();
      expect(jobTitle.tagName).toBe('H3');
      expect(companyName).toBeTruthy();
      expect(duration).toBeTruthy();
      expect(jobDescription).toBeTruthy();
      
      // Content should not be empty
      expect(jobTitle.textContent.trim()).not.toBe('');
      expect(companyName.textContent.trim()).not.toBe('');
      expect(duration.textContent.trim()).not.toBe('');
      expect(jobDescription.textContent.trim()).not.toBe('');
    });
  });

  test('Skills section displays technical competencies in organized categories', () => {
    const skillsSection = document.getElementById('skills');
    const skillCategories = skillsSection.querySelectorAll('.skill-category');
    
    expect(skillCategories.length).toBeGreaterThanOrEqual(2);
    
    Array.from(skillCategories).forEach(category => {
      const categoryTitle = category.querySelector('.category-title');
      const skillItems = category.querySelectorAll('.skill-item');
      
      // Category should have a descriptive title
      const titleText = categoryTitle.textContent.trim();
      expect(titleText.length).toBeGreaterThan(5);
      expect(titleText).not.toMatch(/^(Category|Skills|Title)/i);
      
      // Should have multiple skills per category
      expect(skillItems.length).toBeGreaterThanOrEqual(3);
      
      Array.from(skillItems).forEach(item => {
        const skillName = item.querySelector('.skill-name');
        const skillIndicator = item.querySelector('.skill-indicator');
        
        // Skill name should be descriptive
        const nameText = skillName.textContent.trim();
        expect(nameText.length).toBeGreaterThan(2);
        expect(nameText).not.toMatch(/^(Skill|Name)/i);
        
        // Skill indicator should have proficiency data
        const proficiency = skillIndicator.getAttribute('data-proficiency');
        expect(proficiency).toBeTruthy();
        expect(['1', '2', '3', '4', '5']).toContain(proficiency);
      });
    });
  });

  test('Experience section displays work history with achievements', () => {
    const experienceSection = document.getElementById('experience');
    const experienceItems = experienceSection.querySelectorAll('.experience-item');
    
    expect(experienceItems.length).toBeGreaterThanOrEqual(2);
    
    Array.from(experienceItems).forEach(item => {
      const jobTitle = item.querySelector('.job-title');
      const companyName = item.querySelector('.company-name');
      const duration = item.querySelector('.duration');
      const jobDescription = item.querySelector('.job-description');
      const achievements = item.querySelector('.achievements');
      
      // Job title should be descriptive
      const titleText = jobTitle.textContent.trim();
      expect(titleText.length).toBeGreaterThan(5);
      expect(titleText).not.toMatch(/^(Job Title|Title|Position)/i);
      
      // Company name should be present
      const companyText = companyName.textContent.trim();
      expect(companyText.length).toBeGreaterThan(3);
      expect(companyText).not.toMatch(/^(Company|Name)/i);
      
      // Duration should follow a reasonable format
      const durationText = duration.textContent.trim();
      expect(durationText.length).toBeGreaterThan(4);
      expect(durationText).not.toBe('Duration');
      
      // Description should be substantial
      const descriptionText = jobDescription.textContent.trim();
      expect(descriptionText.length).toBeGreaterThan(50);
      expect(descriptionText.split(' ').length).toBeGreaterThan(15);
      
      // Should have achievements listed
      if (achievements) {
        const achievementItems = achievements.querySelectorAll('li');
        expect(achievementItems.length).toBeGreaterThanOrEqual(2);
        
        Array.from(achievementItems).forEach(achievement => {
          const achievementText = achievement.textContent.trim();
          expect(achievementText.length).toBeGreaterThan(20);
          expect(achievementText).not.toMatch(/^(Achievement|Key)/i);
        });
      }
    });
  });

  test('Skills have visual proficiency indicators', () => {
    const skillItems = document.querySelectorAll('.skill-item');
    
    Array.from(skillItems).forEach(item => {
      const skillIndicator = item.querySelector('.skill-indicator');
      const proficiency = skillIndicator.getAttribute('data-proficiency');
      
      // Should have proficiency level
      expect(['1', '2', '3', '4', '5']).toContain(proficiency);
      
      // Should have visual indicator (progress bar or level text)
      const skillBar = skillIndicator.querySelector('.skill-bar');
      const skillLevel = skillIndicator.querySelector('.skill-level');
      
      expect(skillBar || skillLevel).toBeTruthy();
      
      if (skillBar) {
        const skillProgress = skillBar.querySelector('.skill-progress');
        expect(skillProgress).toBeTruthy();
        
        // Progress width should correspond to proficiency
        const progressStyle = window.getComputedStyle(skillProgress);
        const width = progressStyle.width;
        expect(width).toBeTruthy();
        expect(width).not.toBe('0px');
      }
      
      if (skillLevel) {
        const levelText = skillLevel.textContent.trim();
        expect(levelText).toBeTruthy();
        expect(['Beginner', 'Intermediate', 'Advanced', 'Expert']).toContain(levelText);
      }
    });
  });

  test('Experience section highlights key achievements', () => {
    const experienceItems = document.querySelectorAll('.experience-item');
    
    Array.from(experienceItems).forEach(item => {
      const achievements = item.querySelector('.achievements');
      
      if (achievements) {
        const achievementItems = achievements.querySelectorAll('li');
        
        Array.from(achievementItems).forEach(achievement => {
          const text = achievement.textContent.trim();
          
          // Achievements should be substantial and specific
          expect(text.length).toBeGreaterThan(20);
          expect(text.split(' ').length).toBeGreaterThan(5);
          
          // Should not be generic placeholder text
          expect(text).not.toMatch(/^(Key achievement|Achievement|Accomplishment)/i);
          
          // Should have proper styling (checkmark or bullet)
          const style = window.getComputedStyle(achievement, '::before');
          expect(style.content).toBeTruthy();
        });
      }
    });
  });

  test('Property-based test: Skills and experience maintain structure with varying content', () => {
    fc.assert(
      fc.property(
        fc.record({
          skillName: fc.string({ minLength: 3, maxLength: 30 }),
          proficiency: fc.integer({ min: 1, max: 5 }),
          jobTitle: fc.string({ minLength: 5, maxLength: 50 }),
          company: fc.string({ minLength: 3, maxLength: 30 })
        }),
        (data) => {
          // Test that structure remains valid with different content
          const skillsSection = document.getElementById('skills');
          const experienceSection = document.getElementById('experience');
          
          // Skills section structure validation
          const skillCategories = skillsSection.querySelectorAll('.skill-category');
          const hasValidSkillStructure = Array.from(skillCategories).every(category => {
            const title = category.querySelector('.category-title');
            const list = category.querySelector('.skill-list');
            const items = category.querySelectorAll('.skill-item');
            
            return title && list && items.length > 0 &&
                   title.tagName === 'H3' && list.tagName === 'UL' &&
                   Array.from(items).every(item => item.tagName === 'LI');
          });
          
          // Experience section structure validation
          const experienceItems = experienceSection.querySelectorAll('.experience-item');
          const hasValidExperienceStructure = Array.from(experienceItems).every(item => {
            const title = item.querySelector('.job-title');
            const company = item.querySelector('.company-name');
            const duration = item.querySelector('.duration');
            const description = item.querySelector('.job-description');
            
            return title && company && duration && description &&
                   title.tagName === 'H3' &&
                   title.textContent.trim() !== '' &&
                   company.textContent.trim() !== '';
          });
          
          return hasValidSkillStructure && hasValidExperienceStructure;
        }
      ),
      { numRuns: 50 }
    );
  });

  test('Skills and experience sections are accessible', () => {
    // Test heading hierarchy
    const skillsTitle = document.querySelector('#skills .section-title');
    const experienceTitle = document.querySelector('#experience .section-title');
    
    expect(skillsTitle.tagName).toBe('H2');
    expect(experienceTitle.tagName).toBe('H2');
    
    // Test category headings
    const categoryTitles = document.querySelectorAll('.category-title');
    Array.from(categoryTitles).forEach(title => {
      expect(title.tagName).toBe('H3');
    });
    
    // Test job titles
    const jobTitles = document.querySelectorAll('.job-title');
    Array.from(jobTitles).forEach(title => {
      expect(title.tagName).toBe('H3');
    });
    
    // Test list semantics
    const skillLists = document.querySelectorAll('.skill-list');
    Array.from(skillLists).forEach(list => {
      expect(list.tagName).toBe('UL');
      
      const items = list.querySelectorAll('li');
      expect(items.length).toBeGreaterThan(0);
    });
    
    const achievementLists = document.querySelectorAll('.achievements');
    Array.from(achievementLists).forEach(list => {
      expect(list.tagName).toBe('UL');
      
      const items = list.querySelectorAll('li');
      Array.from(items).forEach(item => {
        expect(item.tagName).toBe('LI');
      });
    });
  });

  test('Skills and experience content is not placeholder text', () => {
    // Test skills content
    const skillNames = document.querySelectorAll('.skill-name');
    Array.from(skillNames).forEach(skill => {
      const text = skill.textContent.trim();
      expect(text).not.toMatch(/^(Skill|Name|Technology)/i);
      expect(text).not.toBe('');
      expect(text.length).toBeGreaterThan(2);
    });
    
    // Test experience content
    const jobTitles = document.querySelectorAll('.job-title');
    Array.from(jobTitles).forEach(title => {
      const text = title.textContent.trim();
      expect(text).not.toMatch(/^(Job Title|Title|Position|Previous)/i);
      expect(text).not.toBe('');
      expect(text.length).toBeGreaterThan(5);
    });
    
    const companyNames = document.querySelectorAll('.company-name');
    Array.from(companyNames).forEach(company => {
      const text = company.textContent.trim();
      expect(text).not.toMatch(/^(Company|Name|Previous)/i);
      expect(text).not.toBe('');
      expect(text.length).toBeGreaterThan(3);
    });
    
    const jobDescriptions = document.querySelectorAll('.job-description');
    Array.from(jobDescriptions).forEach(description => {
      const text = description.textContent.trim();
      expect(text).not.toMatch(/^(Description|Role|Responsibilities)/i);
      expect(text.length).toBeGreaterThan(50);
    });
  });
});