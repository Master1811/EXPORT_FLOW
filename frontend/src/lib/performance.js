/**
 * Performance Monitoring Utilities
 * Track and report performance metrics for optimization
 */

// Performance observer for monitoring
let performanceObserver = null;

/**
 * Initialize performance monitoring
 */
export function initPerformanceMonitoring() {
  if (typeof window === 'undefined' || !window.PerformanceObserver) {
    return;
  }

  // Track long tasks (>50ms)
  try {
    performanceObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach((entry) => {
        if (entry.duration > 100) {
          console.warn(`[Performance] Long task detected: ${entry.duration.toFixed(2)}ms`);
        }
      });
    });
    performanceObserver.observe({ entryTypes: ['longtask'] });
  } catch (e) {
    // Long task observer not supported
  }

  // Track largest contentful paint
  try {
    const lcpObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const lastEntry = entries[entries.length - 1];
      if (lastEntry) {
        console.log(`[Performance] LCP: ${lastEntry.startTime.toFixed(2)}ms`);
      }
    });
    lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
  } catch (e) {
    // LCP observer not supported
  }

  // Track first input delay
  try {
    const fidObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach((entry) => {
        console.log(`[Performance] FID: ${entry.processingStart - entry.startTime}ms`);
      });
    });
    fidObserver.observe({ entryTypes: ['first-input'] });
  } catch (e) {
    // FID observer not supported
  }
}

/**
 * Measure component render time
 */
export function measureRender(componentName, callback) {
  const start = performance.now();
  const result = callback();
  const end = performance.now();
  
  if (end - start > 16) { // More than one frame (16ms at 60fps)
    console.warn(`[Performance] ${componentName} render took ${(end - start).toFixed(2)}ms`);
  }
  
  return result;
}

/**
 * Measure async operation time
 */
export async function measureAsync(operationName, asyncCallback) {
  const start = performance.now();
  try {
    const result = await asyncCallback();
    const end = performance.now();
    
    if (end - start > 1000) {
      console.warn(`[Performance] ${operationName} took ${(end - start).toFixed(2)}ms`);
    }
    
    return result;
  } catch (error) {
    const end = performance.now();
    console.error(`[Performance] ${operationName} failed after ${(end - start).toFixed(2)}ms`);
    throw error;
  }
}

/**
 * Report Web Vitals metrics
 */
export function reportWebVitals(metric) {
  // In production, send to analytics service
  if (process.env.NODE_ENV === 'development') {
    console.log(`[WebVitals] ${metric.name}: ${metric.value}`);
  }
}

/**
 * Track memory usage (Chrome only)
 */
export function getMemoryUsage() {
  if (performance.memory) {
    return {
      usedJSHeapSize: (performance.memory.usedJSHeapSize / 1048576).toFixed(2) + ' MB',
      totalJSHeapSize: (performance.memory.totalJSHeapSize / 1048576).toFixed(2) + ' MB',
      jsHeapSizeLimit: (performance.memory.jsHeapSizeLimit / 1048576).toFixed(2) + ' MB',
    };
  }
  return null;
}

/**
 * Debounce function for performance-critical operations
 */
export function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Throttle function for rate-limiting
 */
export function throttle(func, limit) {
  let inThrottle;
  return function executedFunction(...args) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

/**
 * Request idle callback wrapper with fallback
 */
export function requestIdleCallback(callback, options = {}) {
  if (typeof window !== 'undefined' && window.requestIdleCallback) {
    return window.requestIdleCallback(callback, options);
  }
  // Fallback for browsers without requestIdleCallback
  return setTimeout(() => callback({ didTimeout: false, timeRemaining: () => 50 }), 1);
}

/**
 * Cancel idle callback
 */
export function cancelIdleCallback(id) {
  if (typeof window !== 'undefined' && window.cancelIdleCallback) {
    window.cancelIdleCallback(id);
  } else {
    clearTimeout(id);
  }
}

export default {
  initPerformanceMonitoring,
  measureRender,
  measureAsync,
  reportWebVitals,
  getMemoryUsage,
  debounce,
  throttle,
  requestIdleCallback,
  cancelIdleCallback,
};
