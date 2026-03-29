/**
 * Personal Profile Website - Main JavaScript Functionality
 * Implements smooth scrolling navigation and interactive features
 */

(function() {
  'use strict';

  // DOM elements
  const nav = document.querySelector('.nav');
  const navLinks = document.querySelectorAll('.nav-link');
  const sections = document.querySelectorAll('.section');
  const scrollIndicator = document.querySelector('.scroll-indicator');
  
  // Configuration
  const config = {
    scrollOffset: 80, // Offset for fixed navigation
    scrollDuration: 800, // Smooth scroll duration in ms
    activeClassThreshold: 0.3 // Percentage of section visible to be considered active
  };

  /**
   * Initialize the application
   */
  function init() {
    setupSmoothScrolling();
    setupNavigationHighlighting();
    setupScrollIndicator();
    setupNavigationBackground();
    setupErrorHandling();
    
    // Add loaded class for animations
    document.body.classList.add('loaded');
  }

  /**
   * Set up smooth scrolling for navigation links
   */
  function setupSmoothScrolling() {
    navLinks.forEach(link => {
      link.addEventListener('click', handleNavClick);
    });
  }

  /**
   * Handle navigation link clicks
   * @param {Event} event - Click event
   */
  function handleNavClick(event) {
    event.preventDefault();
    
    const targetId = event.target.getAttribute('href');
    const targetSection = document.querySelector(targetId);
    
    if (targetSection) {
      smoothScrollTo(targetSection);
      
      // Update URL without triggering scroll
      if (history.pushState) {
        history.pushState(null, null, targetId);
      }
    }
  }

  /**
   * Smooth scroll to target element
   * @param {Element} target - Target element to scroll to
   */
  function smoothScrollTo(target) {
    const targetPosition = target.offsetTop - config.scrollOffset;
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition;
    const startTime = performance.now();

    function scrollAnimation(currentTime) {
      const timeElapsed = currentTime - startTime;
      const progress = Math.min(timeElapsed / config.scrollDuration, 1);
      
      // Easing function (ease-in-out)
      const easeInOutCubic = progress < 0.5 
        ? 4 * progress * progress * progress 
        : (progress - 1) * (2 * progress - 2) * (2 * progress - 2) + 1;
      
      window.scrollTo(0, startPosition + distance * easeInOutCubic);
      
      if (progress < 1) {
        requestAnimationFrame(scrollAnimation);
      }
    }
    
    requestAnimationFrame(scrollAnimation);
  }

  /**
   * Set up navigation highlighting based on scroll position
   */
  function setupNavigationHighlighting() {
    let ticking = false;
    
    function updateActiveNavigation() {
      const scrollPosition = window.pageYOffset + config.scrollOffset + 100;
      let activeSection = null;
      
      // Find the currently active section
      sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.offsetHeight;
        const sectionBottom = sectionTop + sectionHeight;
        
        if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
          activeSection = section;
        }
      });
      
      // Update navigation links
      navLinks.forEach(link => {
        link.classList.remove('active');
        
        if (activeSection) {
          const targetId = link.getAttribute('href');
          if (targetId === `#${activeSection.id}`) {
            link.classList.add('active');
          }
        }
      });
      
      ticking = false;
    }
    
    function requestTick() {
      if (!ticking) {
        requestAnimationFrame(updateActiveNavigation);
        ticking = true;
      }
    }
    
    window.addEventListener('scroll', requestTick);
    window.addEventListener('resize', requestTick);
    
    // Initial call
    updateActiveNavigation();
  }

  /**
   * Set up scroll indicator functionality
   */
  function setupScrollIndicator() {
    if (scrollIndicator) {
      scrollIndicator.addEventListener('click', () => {
        const aboutSection = document.getElementById('about');
        if (aboutSection) {
          smoothScrollTo(aboutSection);
        }
      });
      
      // Hide scroll indicator when user scrolls
      let hideTimeout;
      window.addEventListener('scroll', () => {
        if (window.pageYOffset > 100) {
          scrollIndicator.style.opacity = '0';
          scrollIndicator.style.pointerEvents = 'none';
        } else {
          scrollIndicator.style.opacity = '1';
          scrollIndicator.style.pointerEvents = 'auto';
        }
      });
    }
  }

  /**
   * Set up navigation background changes on scroll
   */
  function setupNavigationBackground() {
    if (nav) {
      let ticking = false;
      
      function updateNavigationBackground() {
        const scrolled = window.pageYOffset > 50;
        nav.classList.toggle('scrolled', scrolled);
        ticking = false;
      }
      
      function requestTick() {
        if (!ticking) {
          requestAnimationFrame(updateNavigationBackground);
          ticking = true;
        }
      }
      
      window.addEventListener('scroll', requestTick);
    }
  }

  /**
   * Set up error handling for images and other resources
   */
  function setupErrorHandling() {
    // Handle profile photo loading errors
    const profilePhoto = document.querySelector('.profile-photo');
    const profilePhotoFallback = document.querySelector('.profile-photo-fallback');
    
    if (profilePhoto && profilePhotoFallback) {
      profilePhoto.addEventListener('error', () => {
        profilePhoto.style.display = 'none';
        profilePhotoFallback.style.display = 'flex';
      });
      
      profilePhoto.addEventListener('load', () => {
        profilePhoto.style.display = 'block';
        profilePhotoFallback.style.display = 'none';
      });
    }
    
    // Handle other image errors
    const images = document.querySelectorAll('img:not(.profile-photo)');
    images.forEach(img => {
      img.addEventListener('error', function() {
        this.style.opacity = '0.5';
        this.alt = 'Image failed to load';
      });
    });
  }

  /**
   * Utility function to debounce function calls
   * @param {Function} func - Function to debounce
   * @param {number} wait - Wait time in milliseconds
   * @param {boolean} immediate - Execute immediately
   * @returns {Function} Debounced function
   */
  function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        timeout = null;
        if (!immediate) func.apply(this, args);
      };
      const callNow = immediate && !timeout;
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
      if (callNow) func.apply(this, args);
    };
  }

  /**
   * Utility function to throttle function calls
   * @param {Function} func - Function to throttle
   * @param {number} limit - Time limit in milliseconds
   * @returns {Function} Throttled function
   */
  function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }

  /**
   * Check if element is in viewport
   * @param {Element} element - Element to check
   * @param {number} threshold - Visibility threshold (0-1)
   * @returns {boolean} Whether element is visible
   */
  function isElementInViewport(element, threshold = 0.1) {
    const rect = element.getBoundingClientRect();
    const windowHeight = window.innerHeight || document.documentElement.clientHeight;
    const windowWidth = window.innerWidth || document.documentElement.clientWidth;
    
    const vertInView = (rect.top <= windowHeight) && ((rect.top + rect.height) >= 0);
    const horInView = (rect.left <= windowWidth) && ((rect.left + rect.width) >= 0);
    
    return vertInView && horInView;
  }

  /**
   * Add CSS class for enhanced navigation styling
   */
  function addNavigationStyles() {
    const style = document.createElement('style');
    style.textContent = `
      .nav.scrolled {
        background-color: rgba(44, 62, 80, 0.98);
        backdrop-filter: blur(15px);
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
      }
      
      .nav-link.active {
        background-color: rgba(255, 255, 255, 0.15);
        color: #ffffff;
      }
      
      .nav-link.active::after {
        width: 100%;
      }
      
      body.loaded .hero-content > * {
        opacity: 1;
        transform: translateY(0);
      }
      
      @media (prefers-reduced-motion: reduce) {
        .hero-content > * {
          animation: none !important;
        }
      }
    `;
    document.head.appendChild(style);
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
  
  // Add navigation styles
  addNavigationStyles();

  // Export functions for testing
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
      smoothScrollTo,
      isElementInViewport,
      debounce,
      throttle
    };
  }

})();
  /**
   * Set up contact link functionality and analytics
   */
  function setupContactLinks() {
    // Email links
    const emailLinks = document.querySelectorAll('a[href^="mailto:"]');
    emailLinks.forEach(link => {
      link.addEventListener('click', function(event) {
        // Track email click (for analytics if needed)
        console.log('Email link clicked:', this.href);
        
        // Check if email client is available
        if (!navigator.userAgent.includes('Mobile')) {
          // On desktop, show a helpful message
          const email = this.href.replace('mailto:', '');
          if (confirm(`This will open your default email client to send an email to ${email}. Continue?`)) {
            // Let the default action proceed
            return true;
          } else {
            event.preventDefault();
            // Copy email to clipboard as fallback
            copyToClipboard(email);
            showNotification('Email address copied to clipboard!');
          }
        }
      });
    });
    
    // Phone links
    const phoneLinks = document.querySelectorAll('a[href^="tel:"]');
    phoneLinks.forEach(link => {
      link.addEventListener('click', function(event) {
        console.log('Phone link clicked:', this.href);
        
        // On desktop, show phone number and copy to clipboard
        if (!navigator.userAgent.includes('Mobile')) {
          event.preventDefault();
          const phone = this.textContent.trim();
          copyToClipboard(phone);
          showNotification(`Phone number ${phone} copied to clipboard!`);
        }
      });
    });
    
    // Social media links
    const socialLinks = document.querySelectorAll('.social-link[target="_blank"]');
    socialLinks.forEach(link => {
      link.addEventListener('click', function() {
        const platform = this.querySelector('.social-text').textContent;
        console.log(`${platform} link clicked:`, this.href);
      });
    });
    
    // CTA button
    const ctaButton = document.querySelector('.cta-button');
    if (ctaButton) {
      ctaButton.addEventListener('click', function() {
        console.log('CTA button clicked:', this.href);
      });
    }
  }
  
  /**
   * Copy text to clipboard
   * @param {string} text - Text to copy
   */
  function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).catch(err => {
        console.error('Failed to copy to clipboard:', err);
        fallbackCopyToClipboard(text);
      });
    } else {
      fallbackCopyToClipboard(text);
    }
  }
  
  /**
   * Fallback copy to clipboard method
   * @param {string} text - Text to copy
   */
  function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
      document.execCommand('copy');
    } catch (err) {
      console.error('Fallback copy failed:', err);
    }
    
    document.body.removeChild(textArea);
  }
  
  /**
   * Show notification message
   * @param {string} message - Message to show
   */
  function showNotification(message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: var(--secondary-color);
      color: var(--text-light);
      padding: var(--spacing-md) var(--spacing-lg);
      border-radius: var(--border-radius);
      box-shadow: 0 4px 12px var(--shadow-medium);
      z-index: 1000;
      font-weight: 500;
      transform: translateX(100%);
      transition: transform var(--transition-normal);
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
      notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
      notification.style.transform = 'translateX(100%)';
      setTimeout(() => {
        if (notification.parentNode) {
          document.body.removeChild(notification);
        }
      }, 300);
    }, 3000);
  }
  
  /**
   * Validate email addresses
   * @param {string} email - Email to validate
   * @returns {boolean} Whether email is valid
   */
  function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
  
  /**
   * Validate phone numbers
   * @param {string} phone - Phone to validate
   * @returns {boolean} Whether phone is valid
   */
  function isValidPhone(phone) {
    const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
    const cleanPhone = phone.replace(/[\s\-\(\)]/g, '');
    return phoneRegex.test(cleanPhone);
  }
  
  // Add contact link setup to initialization
  const originalInit = init;
  init = function() {
    originalInit();
    setupContactLinks();
  };