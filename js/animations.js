/**
 * Personal Profile Website - Animation System
 * Implements scroll-triggered animations, hover effects, and performance-optimized transitions
 */

(function() {
  'use strict';

  // Animation configuration
  const config = {
    animationThreshold: 0.1, // Percentage of element visible to trigger animation
    animationDelay: 100, // Base delay between animations in ms
    reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    performanceMode: false // Will be set based on device capabilities
  };

  // Animation state
  let animationObserver = null;
  let isAnimationSystemReady = false;
  let animatedElements = new Set();

  /**
   * Initialize the animation system
   */
  function initAnimations() {
    if (config.reducedMotion) {
      console.log('Reduced motion preference detected, disabling animations');
      return;
    }

    detectPerformanceCapabilities();
    setupIntersectionObserver();
    setupScrollAnimations();
    setupHoverEffects();
    setupLoadingAnimations();
    setupParallaxEffects();
    
    isAnimationSystemReady = true;
    console.log('Animation system initialized');
  }

  /**
   * Detect device performance capabilities
   */
  function detectPerformanceCapabilities() {
    // Check for low-end devices
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    const isSlowConnection = connection && (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g');
    const isLowEndDevice = navigator.hardwareConcurrency && navigator.hardwareConcurrency < 4;
    const hasLimitedMemory = navigator.deviceMemory && navigator.deviceMemory < 4;
    
    config.performanceMode = isSlowConnection || isLowEndDevice || hasLimitedMemory;
    
    if (config.performanceMode) {
      console.log('Performance mode enabled - reducing animation complexity');
    }
  }

  /**
   * Set up intersection observer for scroll-triggered animations
   */
  function setupIntersectionObserver() {
    if (!window.IntersectionObserver) {
      console.warn('IntersectionObserver not supported, falling back to scroll events');
      setupFallbackScrollAnimations();
      return;
    }

    const observerOptions = {
      root: null,
      rootMargin: '0px 0px -10% 0px',
      threshold: config.animationThreshold
    };

    animationObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !animatedElements.has(entry.target)) {
          animateElement(entry.target);
          animatedElements.add(entry.target);
        }
      });
    }, observerOptions);

    // Observe all animatable elements
    const animatableElements = document.querySelectorAll(
      '.about-section, .skills-section, .experience-section, .contact-section, ' +
      '.skill-category, .experience-item, .contact-info, .social-media'
    );

    animatableElements.forEach(element => {
      animationObserver.observe(element);
    });
  }

  /**
   * Animate element when it comes into view
   * @param {Element} element - Element to animate
   */
  function animateElement(element) {
    if (config.reducedMotion || config.performanceMode) {
      element.style.opacity = '1';
      element.style.transform = 'none';
      return;
    }

    // Add animation class
    element.classList.add('animate');

    // Special handling for different element types
    if (element.classList.contains('skills-section')) {
      animateSkillBars(element);
    } else if (element.classList.contains('experience-section')) {
      animateTimeline(element);
    } else if (element.classList.contains('contact-section')) {
      animateContactCards(element);
    }
  }

  /**
   * Animate skill progress bars
   * @param {Element} skillsSection - Skills section element
   */
  function animateSkillBars(skillsSection) {
    const skillBars = skillsSection.querySelectorAll('.skill-progress');
    
    skillBars.forEach((bar, index) => {
      setTimeout(() => {
        const width = bar.style.width || '0%';
        bar.style.width = '0%';
        bar.style.transition = 'width 1.5s ease-out';
        
        // Trigger reflow
        bar.offsetHeight;
        
        // Animate to target width
        bar.style.width = width;
      }, index * 100);
    });
  }

  /**
   * Animate timeline elements
   * @param {Element} experienceSection - Experience section element
   */
  function animateTimeline(experienceSection) {
    const timelineMarkers = experienceSection.querySelectorAll('.timeline-marker');
    
    timelineMarkers.forEach((marker, index) => {
      setTimeout(() => {
        marker.style.transform = 'scale(1)';
        marker.style.opacity = '1';
      }, index * 200);
    });
  }

  /**
   * Animate contact cards
   * @param {Element} contactSection - Contact section element
   */
  function animateContactCards(contactSection) {
    const cards = contactSection.querySelectorAll('.contact-info, .social-media');
    
    cards.forEach((card, index) => {
      setTimeout(() => {
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
      }, index * 200);
    });
  }

  /**
   * Set up scroll-based animations
   */
  function setupScrollAnimations() {
    let ticking = false;
    
    function updateScrollAnimations() {
      const scrolled = window.pageYOffset;
      const windowHeight = window.innerHeight;
      
      // Parallax effect for header
      const header = document.querySelector('.header');
      if (header && !config.performanceMode) {
        const parallaxSpeed = 0.5;
        header.style.transform = `translateY(${scrolled * parallaxSpeed}px)`;
      }
      
      // Update navigation background
      const nav = document.querySelector('.nav');
      if (nav) {
        nav.classList.toggle('scrolled', scrolled > 50);
      }
      
      // Hide/show scroll indicator
      const scrollIndicator = document.querySelector('.scroll-indicator');
      if (scrollIndicator) {
        const opacity = Math.max(0, 1 - (scrolled / windowHeight));
        scrollIndicator.style.opacity = opacity;
        scrollIndicator.style.pointerEvents = opacity > 0.1 ? 'auto' : 'none';
      }
      
      ticking = false;
    }
    
    function requestScrollUpdate() {
      if (!ticking) {
        requestAnimationFrame(updateScrollAnimations);
        ticking = true;
      }
    }
    
    window.addEventListener('scroll', requestScrollUpdate, { passive: true });
    
    // Initial call
    updateScrollAnimations();
  }

  /**
   * Set up hover effects
   */
  function setupHoverEffects() {
    if (config.performanceMode) return;

    // Enhanced hover effects for cards
    const cards = document.querySelectorAll(
      '.skill-category, .experience-card, .contact-info, .social-media'
    );
    
    cards.forEach(card => {
      card.addEventListener('mouseenter', function() {
        if (!config.reducedMotion) {
          this.style.transform = 'translateY(-4px) scale(1.02)';
          this.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        }
      });
      
      card.addEventListener('mouseleave', function() {
        if (!config.reducedMotion) {
          this.style.transform = 'translateY(0) scale(1)';
        }
      });
    });

    // Hover effects for social links
    const socialLinks = document.querySelectorAll('.social-link');
    socialLinks.forEach(link => {
      link.addEventListener('mouseenter', function() {
        if (!config.reducedMotion) {
          const icon = this.querySelector('.social-icon');
          if (icon) {
            icon.style.transform = 'scale(1.2) rotate(5deg)';
            icon.style.transition = 'transform 0.3s ease';
          }
        }
      });
      
      link.addEventListener('mouseleave', function() {
        if (!config.reducedMotion) {
          const icon = this.querySelector('.social-icon');
          if (icon) {
            icon.style.transform = 'scale(1) rotate(0deg)';
          }
        }
      });
    });

    // Hover effects for skill bars
    const skillItems = document.querySelectorAll('.skill-item');
    skillItems.forEach(item => {
      item.addEventListener('mouseenter', function() {
        if (!config.reducedMotion) {
          const progress = this.querySelector('.skill-progress');
          if (progress) {
            progress.style.boxShadow = '0 0 10px rgba(52, 152, 219, 0.5)';
            progress.style.transition = 'box-shadow 0.3s ease';
          }
        }
      });
      
      item.addEventListener('mouseleave', function() {
        if (!config.reducedMotion) {
          const progress = this.querySelector('.skill-progress');
          if (progress) {
            progress.style.boxShadow = 'none';
          }
        }
      });
    });
  }

  /**
   * Set up loading animations
   */
  function setupLoadingAnimations() {
    // Animate hero content on load
    const heroContent = document.querySelector('.hero-content');
    if (heroContent && !config.reducedMotion) {
      const children = heroContent.children;
      
      Array.from(children).forEach((child, index) => {
        child.style.opacity = '0';
        child.style.transform = 'translateY(30px)';
        child.style.transition = `opacity 0.8s ease ${index * 0.1}s, transform 0.8s ease ${index * 0.1}s`;
        
        setTimeout(() => {
          child.style.opacity = '1';
          child.style.transform = 'translateY(0)';
        }, 100);
      });
    }

    // Animate navigation links
    const navLinks = document.querySelectorAll('.nav-link');
    if (!config.reducedMotion) {
      navLinks.forEach((link, index) => {
        link.style.opacity = '0';
        link.style.transform = 'translateY(-20px)';
        link.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;
        
        setTimeout(() => {
          link.style.opacity = '1';
          link.style.transform = 'translateY(0)';
        }, 200);
      });
    }
  }

  /**
   * Set up parallax effects
   */
  function setupParallaxEffects() {
    if (config.performanceMode || config.reducedMotion) return;

    let ticking = false;
    
    function updateParallax() {
      const scrolled = window.pageYOffset;
      
      // Subtle parallax for section backgrounds
      const sections = document.querySelectorAll('.section:nth-child(even)');
      sections.forEach((section, index) => {
        const speed = 0.1 + (index * 0.05);
        const yPos = -(scrolled * speed);
        section.style.transform = `translateY(${yPos}px)`;
      });
      
      ticking = false;
    }
    
    function requestParallaxUpdate() {
      if (!ticking) {
        requestAnimationFrame(updateParallax);
        ticking = true;
      }
    }
    
    window.addEventListener('scroll', requestParallaxUpdate, { passive: true });
  }

  /**
   * Fallback scroll animations for older browsers
   */
  function setupFallbackScrollAnimations() {
    let ticking = false;
    
    function checkElementsInView() {
      const elements = document.querySelectorAll(
        '.about-section, .skills-section, .experience-section, .contact-section'
      );
      
      elements.forEach(element => {
        if (animatedElements.has(element)) return;
        
        const rect = element.getBoundingClientRect();
        const windowHeight = window.innerHeight;
        
        if (rect.top < windowHeight * 0.8) {
          animateElement(element);
          animatedElements.add(element);
        }
      });
      
      ticking = false;
    }
    
    function requestFallbackUpdate() {
      if (!ticking) {
        requestAnimationFrame(checkElementsInView);
        ticking = true;
      }
    }
    
    window.addEventListener('scroll', requestFallbackUpdate, { passive: true });
    
    // Initial check
    checkElementsInView();
  }

  /**
   * Handle visibility change to pause/resume animations
   */
  function handleVisibilityChange() {
    if (document.hidden) {
      // Pause animations when tab is not visible
      document.body.style.animationPlayState = 'paused';
    } else {
      // Resume animations when tab becomes visible
      document.body.style.animationPlayState = 'running';
    }
  }

  /**
   * Clean up animation resources
   */
  function cleanup() {
    if (animationObserver) {
      animationObserver.disconnect();
    }
    
    animatedElements.clear();
  }

  /**
   * Public API
   */
  window.AnimationSystem = {
    init: initAnimations,
    cleanup: cleanup,
    isReady: () => isAnimationSystemReady,
    config: config
  };

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAnimations);
  } else {
    initAnimations();
  }

  // Handle visibility changes
  document.addEventListener('visibilitychange', handleVisibilityChange);

  // Handle reduced motion preference changes
  const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  mediaQuery.addListener((e) => {
    config.reducedMotion = e.matches;
    if (e.matches) {
      // Disable all animations
      document.body.classList.add('reduce-motion');
    } else {
      document.body.classList.remove('reduce-motion');
    }
  });

  // Clean up on page unload
  window.addEventListener('beforeunload', cleanup);

})();