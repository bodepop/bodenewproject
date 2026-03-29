/**
 * Resource Optimization System
 * Handles resource preloading, compression detection, and performance optimization
 */

(function() {
  'use strict';

  // Configuration
  const config = {
    enableResourceHints: true,
    enableServiceWorker: false, // Disabled for static hosting
    enableCompression: true,
    criticalResourceTimeout: 3000,
    preloadCriticalResources: true
  };

  /**
   * Initialize resource optimization
   */
  function initResourceOptimization() {
    detectBrowserCapabilities();
    preloadCriticalResources();
    optimizeResourceLoading();
    setupPerformanceMonitoring();
    
    console.log('Resource optimization initialized');
  }

  /**
   * Detect browser capabilities for optimization
   */
  function detectBrowserCapabilities() {
    // Check for modern features
    const capabilities = {
      webp: checkWebPSupport(),
      avif: checkAVIFSupport(),
      preload: 'preload' in document.createElement('link'),
      prefetch: 'prefetch' in document.createElement('link'),
      moduleScripts: 'noModule' in document.createElement('script'),
      intersectionObserver: 'IntersectionObserver' in window,
      serviceWorker: 'serviceWorker' in navigator
    };

    // Add capability classes to document
    Object.keys(capabilities).forEach(capability => {
      if (capabilities[capability]) {
        document.documentElement.classList.add(capability);
      }
    });

    console.log('Browser capabilities detected:', capabilities);
    return capabilities;
  }

  /**
   * Check WebP support
   */
  function checkWebPSupport() {
    return new Promise(resolve => {
      const webP = new Image();
      webP.onload = webP.onerror = () => resolve(webP.height === 2);
      webP.src = 'data:image/webp;base64,UklGRjoAAABXRUJQVlA4IC4AAACyAgCdASoCAAIALmk0mk0iIiIiIgBoSygABc6WWgAA/veff/0PP8bA//LwYAAA';
    });
  }

  /**
   * Check AVIF support
   */
  function checkAVIFSupport() {
    return new Promise(resolve => {
      const avif = new Image();
      avif.onload = avif.onerror = () => resolve(avif.height === 2);
      avif.src = 'data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADybWV0YQAAAAAAAAAoaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAGxpYmF2aWYAAAAADnBpdG0AAAAAAAEAAAAeaWxvYwAAAABEAAABAAEAAAABAAABGgAAAB0AAAAoaWluZgAAAAAAAQAAABppbmZlAgAAAAABAABhdjAxQ29sb3IAAAAAamlwcnAAAABLaXBjbwAAABRpc3BlAAAAAAAAAAIAAAACAAAAEHBpeGkAAAAAAwgICAAAAAxhdjFDgQ0MAAAAABNjb2xybmNseAACAAIAAYAAAAAXaXBtYQAAAAAAAAABAAEEAQKDBAAAACVtZGF0EgAKCBgABogQEAwgMg8f8D///8WfhwB8+ErK42A=';
    });
  }

  /**
   * Preload critical resources
   */
  function preloadCriticalResources() {
    if (!config.preloadCriticalResources) return;

    const criticalResources = [
      { href: 'css/styles.min.css', as: 'style', type: 'text/css' },
      { href: 'css/responsive.min.css', as: 'style', type: 'text/css' },
      { href: 'js/main.min.js', as: 'script', type: 'text/javascript' },
      { href: 'images/profile-placeholder.svg', as: 'image', type: 'image/svg+xml' }
    ];

    criticalResources.forEach(resource => {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.href = resource.href;
      link.as = resource.as;
      if (resource.type) link.type = resource.type;
      link.crossOrigin = 'anonymous';
      
      // Add error handling
      link.onerror = () => console.warn(`Failed to preload: ${resource.href}`);
      
      document.head.appendChild(link);
    });

    console.log('Critical resources preloaded');
  }

  /**
   * Optimize resource loading based on connection and device
   */
  function optimizeResourceLoading() {
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    
    if (connection) {
      const isSlowConnection = connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g';
      const isDataSaver = connection.saveData;
      
      if (isSlowConnection || isDataSaver) {
        console.log('Slow connection detected, optimizing resources');
        
        // Disable non-critical animations
        document.documentElement.classList.add('reduce-animations');
        
        // Use smaller images
        optimizeImagesForSlowConnection();
        
        // Defer non-critical scripts
        deferNonCriticalScripts();
      }
    }

    // Optimize based on device memory
    if (navigator.deviceMemory && navigator.deviceMemory < 4) {
      console.log('Low memory device detected');
      document.documentElement.classList.add('low-memory');
    }
  }

  /**
   * Optimize images for slow connections
   */
  function optimizeImagesForSlowConnection() {
    const images = document.querySelectorAll('img[data-src]');
    images.forEach(img => {
      if (img.dataset.srcSmall) {
        img.dataset.src = img.dataset.srcSmall;
      }
    });
  }

  /**
   * Defer non-critical scripts
   */
  function deferNonCriticalScripts() {
    const nonCriticalScripts = document.querySelectorAll('script[data-defer]');
    nonCriticalScripts.forEach(script => {
      script.defer = true;
    });
  }

  /**
   * Setup performance monitoring
   */
  function setupPerformanceMonitoring() {
    if (!window.performance || !window.performance.mark) return;

    // Mark critical points
    performance.mark('resource-optimization-start');

    // Monitor page load performance
    window.addEventListener('load', () => {
      performance.mark('resource-optimization-complete');
      
      setTimeout(() => {
        const perfData = performance.getEntriesByType('navigation')[0];
        if (perfData) {
          console.log('Performance metrics:', {
            domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
            loadComplete: perfData.loadEventEnd - perfData.loadEventStart,
            totalTime: perfData.loadEventEnd - perfData.fetchStart
          });
        }
      }, 0);
    });

    // Monitor resource loading
    const observer = new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        if (entry.duration > 1000) {
          console.warn(`Slow resource detected: ${entry.name} (${entry.duration}ms)`);
        }
      });
    });

    observer.observe({ entryTypes: ['resource'] });
  }

  /**
   * Add resource hints for external domains
   */
  function addResourceHints() {
    if (!config.enableResourceHints) return;

    const hints = [
      { rel: 'dns-prefetch', href: '//fonts.googleapis.com' },
      { rel: 'dns-prefetch', href: '//fonts.gstatic.com' },
      { rel: 'preconnect', href: 'https://fonts.googleapis.com', crossorigin: true },
      { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: true }
    ];

    hints.forEach(hint => {
      const link = document.createElement('link');
      link.rel = hint.rel;
      link.href = hint.href;
      if (hint.crossorigin) link.crossOrigin = 'anonymous';
      document.head.appendChild(link);
    });
  }

  /**
   * Implement resource compression detection
   */
  function setupCompressionDetection() {
    if (!config.enableCompression) return;

    // Check if server supports compression
    fetch('css/styles.min.css', { method: 'HEAD' })
      .then(response => {
        const encoding = response.headers.get('content-encoding');
        if (encoding && (encoding.includes('gzip') || encoding.includes('br'))) {
          console.log('Server compression detected:', encoding);
          document.documentElement.classList.add('compressed');
        }
      })
      .catch(() => {
        console.log('Compression detection failed');
      });
  }

  /**
   * Critical CSS inlining for above-the-fold content
   */
  function inlineCriticalCSS() {
    const criticalCSS = `
      :root{--primary-color:#2c3e50;--secondary-color:#3498db;--text-light:#ecf0f1;--background-primary:#fff;--spacing-md:1rem;--spacing-xl:2rem;--font-size-4xl:2.25rem;--font-size-2xl:1.5rem;--font-size-lg:1.125rem}
      *{margin:0;padding:0;box-sizing:border-box}
      body{font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;color:var(--primary-color);background:var(--background-primary)}
      .header{background:linear-gradient(135deg,var(--primary-color) 0%,var(--secondary-color) 100%);color:var(--text-light);min-height:100vh;display:flex;flex-direction:column}
      .hero{flex:1;display:flex;align-items:center;justify-content:center;text-align:center;padding:var(--spacing-xl) 0}
      .profile-photo{width:200px;height:200px;border-radius:50%;border:4px solid var(--text-light);margin-bottom:var(--spacing-xl)}
      .profile-name{font-size:var(--font-size-4xl);margin-bottom:var(--spacing-md);color:var(--text-light)}
      .profile-title{font-size:var(--font-size-2xl);margin-bottom:var(--spacing-md);color:rgba(255,255,255,.9)}
      .profile-tagline{font-size:var(--font-size-lg);color:rgba(255,255,255,.8)}
    `;

    const style = document.createElement('style');
    style.textContent = criticalCSS;
    document.head.insertBefore(style, document.head.firstChild);
  }

  /**
   * Public API
   */
  window.ResourceOptimizer = {
    init: initResourceOptimization,
    config: config
  };

  // Initialize immediately for critical optimizations
  if (document.readyState === 'loading') {
    // Inline critical CSS immediately
    inlineCriticalCSS();
    
    document.addEventListener('DOMContentLoaded', () => {
      initResourceOptimization();
      addResourceHints();
      setupCompressionDetection();
    });
  } else {
    initResourceOptimization();
    addResourceHints();
    setupCompressionDetection();
  }

})();