import { useState, useCallback, useRef, useEffect } from 'react';

/**
 * Custom hook for API data fetching with caching
 * Reduces redundant API calls and improves perceived performance
 */

// Simple in-memory cache
const cache = new Map();
const CACHE_TTL = 60000; // 1 minute default TTL

export function useApiCache(cacheKey, fetchFn, options = {}) {
  const {
    ttl = CACHE_TTL,
    enabled = true,
    onSuccess,
    onError,
    refetchOnMount = true,
  } = options;

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const isMounted = useRef(true);

  const getCachedData = useCallback(() => {
    const cached = cache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < ttl) {
      return cached.data;
    }
    return null;
  }, [cacheKey, ttl]);

  const setCachedData = useCallback((newData) => {
    cache.set(cacheKey, {
      data: newData,
      timestamp: Date.now(),
    });
  }, [cacheKey]);

  const fetchData = useCallback(async (force = false) => {
    if (!enabled) return;

    // Check cache first (unless forced)
    if (!force) {
      const cachedData = getCachedData();
      if (cachedData) {
        setData(cachedData);
        setLoading(false);
        return cachedData;
      }
    }

    setLoading(true);
    setError(null);

    try {
      const result = await fetchFn();
      if (isMounted.current) {
        setData(result);
        setCachedData(result);
        setLoading(false);
        onSuccess?.(result);
      }
      return result;
    } catch (err) {
      if (isMounted.current) {
        setError(err);
        setLoading(false);
        onError?.(err);
      }
      throw err;
    }
  }, [enabled, fetchFn, getCachedData, setCachedData, onSuccess, onError]);

  const refetch = useCallback(() => fetchData(true), [fetchData]);

  const invalidate = useCallback(() => {
    cache.delete(cacheKey);
  }, [cacheKey]);

  useEffect(() => {
    isMounted.current = true;
    if (refetchOnMount) {
      fetchData();
    }
    return () => {
      isMounted.current = false;
    };
  }, [fetchData, refetchOnMount]);

  return {
    data,
    loading,
    error,
    refetch,
    invalidate,
  };
}

/**
 * Hook for prefetching data on hover
 * Improves perceived navigation speed
 */
export function usePrefetch(fetchFn, cacheKey) {
  const prefetchTimeout = useRef(null);
  const hasPrefetched = useRef(false);

  const prefetch = useCallback(() => {
    if (hasPrefetched.current) return;

    // Delay prefetch slightly to avoid unnecessary requests on quick hovers
    prefetchTimeout.current = setTimeout(async () => {
      try {
        const result = await fetchFn();
        cache.set(cacheKey, {
          data: result,
          timestamp: Date.now(),
        });
        hasPrefetched.current = true;
      } catch (e) {
        // Silently fail prefetch
      }
    }, 100);
  }, [fetchFn, cacheKey]);

  const cancelPrefetch = useCallback(() => {
    if (prefetchTimeout.current) {
      clearTimeout(prefetchTimeout.current);
    }
  }, []);

  return { prefetch, cancelPrefetch };
}

/**
 * Clear all cached data
 */
export function clearCache() {
  cache.clear();
}

/**
 * Clear specific cache entry
 */
export function invalidateCache(key) {
  cache.delete(key);
}

/**
 * Get cache statistics for debugging
 */
export function getCacheStats() {
  return {
    size: cache.size,
    keys: Array.from(cache.keys()),
  };
}

export default useApiCache;
