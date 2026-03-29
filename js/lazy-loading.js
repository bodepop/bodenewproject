/**
 * Lazy Loading System for Images and Content
 * Optimizes performance by loading images only when needed
 */

(function() {
  'use strict';

  // Configuration
  const config = {
    rootMargin: '50px 0px',
    threshold: 0.01,
    enableNativeLazyLoading: 'loading' in HTMLImageElement.prototype,
    placeholderClass: 'lazy-placeholder',
    loadedClass: 'lazy-loaded',
    errorClass: 'lazy-error'
  };

  let lazyImageObserver = null;
  let lazyImages = [];

  /**
   * Initialize lazy loading system
   */
  function initLazyLoading() {
    // Find all images that should be lazy loaded
    lazyImages = Array.from(document.querySelectorAll('img[data-src], img[loading="lazy"]'));
    
    if (lazyImages.length === 0) {
      console.log('No lazy images found');
      return;
    }

    // Use native lazy loading if supported and enabled
    if (config.enableNativeLazyLoading) {
      console.log('Using native lazy loading');
      setupNativeLazyLoading();
    } else {
      console.log('Using Intersection Observer lazy loading');
      setupIntersectionObserverLazyLoading();
    }

    // Setup responsive image loading
    setupResponsiveImages();
    
    // Setup image error handling
    setupImageErrorHandling();
  }

  /**
   * Setup native lazy loading for supported browsers
   */
  function setupNativeLazyLoading() {
    lazyImages.forEach(img => {
      if (img.dataset.src) {
        img.src = img.dataset.src;
        img.loading = 'lazy';
        delete img.dataset.src;
      }
      
      img.addEventListener('load', handleImageLoad);
      img.addEventListener('error', handleImageError);
    });
  }

  /**
   * Setup Intersection Observer based lazy loading
   */
  function setupIntersectionObserverLazyLoading() {
    if (!window.IntersectionObserver) {
      console.warn('IntersectionObserver not supported, loading all images immediately');
      loadAllImages();
      return;
    }

    const observerOptions = {
      root: null,
      rootMargin: config.rootMargin,
      threshold: config.threshold
    };

    lazyImageObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          loadImage(entry.target);
          lazyImageObserver.unobserve(entry.target);
        }
      });
    }, observerOptions);

    lazyImages.forEach(img => {
      lazyImageObserver.observe(img);
      img.classList.add(config.placeholderClass);
    });
  }

  /**
   * Load a single image
   * @param {HTMLImageElement} img - Image element to load
   */
  function loadImage(img) {
    return new Promise((resolve, reject) => {
      const imageLoader = new Image();
      
      imageLoader.onload = () => {
        // Replace src with data-src
        if (img.dataset.src) {
          img.src = img.dataset.src;
          delete img.dataset.src;
        }
        
        // Handle srcset if present
        if (img.dataset.srcset) {
          img.srcset = img.dataset.srcset;
          delete img.dataset.srcset;
        }
        
        handleImageLoad.call(img);
        resolve(img);
      };
      
      imageLoader.onerror = () => {
        handleImageError.call(img);
        reject(new Error(`Failed to load image: ${img.dataset.src || img.src}`));
      };
      
      // Start loading
      imageLoader.src = img.dataset.src || img.src;
      if (img.dataset.srcset) {
        imageLoader.srcset = img.dataset.srcset;
      }
    });
  }

  /**
   * Handle successful image load
   */
  function handleImageLoad() {
    this.classList.remove(config.placeholderClass);
    this.classList.add(config.loadedClass);
    
    // Fade in animation
    this.style.opacity = '0';
    this.style.transition = 'opacity 0.3s ease-in-out';
    
    // Trigger reflow
    this.offsetHeight;
    
    this.style.opacity = '1';
    
    console.log('Image loaded successfully:', this.src);
  }

  /**
   * Handle image load error
   */
  function handleImageError() {
    this.classList.remove(config.placeholderClass);
    this.classList.add(config.errorClass);
    
    // Show fallback or placeholder
    if (this.classList.contains('profile-photo')) {
      // Hide profile photo and show fallback
      this.style.display = 'none';
      const fallback = document.querySelector('.profile-photo-fallback');
      if (fallback) {
        fallback.style.display = 'flex';
      }
    } else {
      // Generic error handling
      this.alt = 'Image failed to load';
      this.style.opacity = '0.5';
      this.style.filter = 'grayscale(100%)';
    }
    
    console.warn('Image failed to load:', this.src || this.dataset.src);
  }

  /**
   * Load all images immediately (fallback)
   */
  function loadAllImages() {
    lazyImages.forEach(img => {
      if (img.dataset.src) {
        img.src = img.dataset.src;
        delete img.dataset.src;
      }
      
      if (img.dataset.srcset) {
        img.srcset = img.dataset.srcset;
        delete img.dataset.srcset;
      }
      
      img.addEventListener('load', handleImageLoad);
      img.addEventListener('error', handleImageError);
    });
  }

  /**
   * Setup responsive images based on viewport size
   */
  function setupResponsiveImages() {
    const profilePhoto = document.querySelector('.profile-photo');
    
    if (profilePhoto) {
      // Create responsive image sources
      const updateProfileImageSrc = () => {
        const viewportWidth = window.innerWidth;
        let imageSrc;
        
        if (viewportWidth < 480) {
          imageSrc = 'images/profile-small.svg';
        } else {
          imageSrc = 'images/profile-placeholder.svg';
        }
        
        // Only update if different
        if (profilePhoto.src !== imageSrc && profilePhoto.dataset.src !== imageSrc) {
          if (profilePhoto.dataset.src) {
            profilePhoto.dataset.src = imageSrc;
          } else {
            profilePhoto.src = imageSrc;
          }
        }
      };
      
      // Update on load and resize
      updateProfileImageSrc();
      window.addEventListener('resize', debounce(updateProfileImageSrc, 250));
    }
  }

  /**
   * Setup comprehensive image error handling
   */
  function setupImageErrorHandling() {
    // Handle all images on the page
    const allImages = document.querySelectorAll('img');
    
    allImages.forEach(img => {
      if (!img.hasAttribute('data-error-handled')) {
        img.addEventListener('error', handleImageError);
        img.setAttribute('data-error-handled', 'true');
      }
    });
  }

  /**
   * Preload critical images
   */
  function preloadCriticalImages() {
    const criticalImages = [
      'images/profile-placeholder.svg',
      'images/profile-small.svg'
    ];
    
    criticalImages.forEach(src => {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.as = 'image';
      link.href = src;
      document.head.appendChild(link);
    });
  }

  /**
   * Optimize image loading based on connection speed
   */
  function optimizeForConnection() {
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    
    if (connection) {
      const isSlowConnection = connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g';
      const isDataSaver = connection.saveData;
      
      if (isSlowConnection || isDataSaver) {
        console.log('Slow connection detected, optimizing image loading');
        
        // Use smaller images
        const images = document.querySelectorAll('img[data-src]');
        images.forEach(img => {
          if (img.dataset.srcSmall) {
            img.dataset.src = img.dataset.srcSmall;
          }
        });
        
        // Increase intersection observer margin for earlier loading
        config.rootMargin = '100px 0px';
      }
    }
  }

  /**
   * Create image placeholder with blur effect
   * @param {HTMLImageElement} img - Image element
   */
  function createBlurPlaceholder(img) {
    if (img.dataset.placeholder) {
      const placeholder = new Image();
      placeholder.src = img.dataset.placeholder;
      placeholder.style.filter = 'blur(5px)';
      placeholder.style.transition = 'filter 0.3s ease';
      
      img.parentNode.insertBefore(placeholder, img);
      
      img.addEventListener('load', () => {
        placeholder.style.filter = 'blur(0px)';
        setTimeout(() => {
          if (placeholder.parentNode) {
            placeholder.parentNode.removeChild(placeholder);
          }
        }, 300);
      });
    }
  }

  /**
   * Debounce utility function
   * @param {Function} func - Function to debounce
   * @param {number} wait - Wait time in milliseconds
   * @returns {Function} Debounced function
   */
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func.apply(this, args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  /**
   * Clean up lazy loading resources
   */
  function cleanup() {
    if (lazyImageObserver) {
      lazyImageObserver.disconnect();
    }
    
    lazyImages = [];
  }

  /**
   * Public API
   */
  window.LazyLoading = {
    init: initLazyLoading,
    loadImage: loadImage,
    cleanup: cleanup,
    config: config
  };

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      optimizeForConnection();
      preloadCriticalImages();
      initLazyLoading();
    });
  } else {
    optimizeForConnection();
    preloadCriticalImages();
    initLazyLoading();
  }

  // Clean up on page unload
  window.addEventListener('beforeunload', cleanup);

})();