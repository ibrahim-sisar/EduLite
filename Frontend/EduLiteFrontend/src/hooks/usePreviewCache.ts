import { useCallback } from 'react';

interface PreviewCacheEntry {
  content: string;
  rendered: string;
  timestamp: number;
}

// In-memory cache shared across all hook instances
// Using Map for better performance than plain object
const previewCache = new Map<string, PreviewCacheEntry>();

const CACHE_EXPIRY = 1000 * 60 * 30; // 30 minutes
const MAX_CACHE_SIZE = 20; // Keep last 20 previews (LRU)

/**
 * Hook for caching markdown preview results in memory
 *
 * Features:
 * - In-memory cache (not localStorage) to avoid storage limits
 * - LRU eviction: keeps last 20 previews
 * - 30-minute expiry per entry
 * - Content-based cache keys (checks if content changed)
 *
 * @param slideId - Unique identifier for the slide (tempId or id)
 * @returns Cache getter and setter functions
 */
export function usePreviewCache(slideId: string) {
  /**
   * Get cached preview if it exists and is valid
   * Returns null if:
   * - No cache entry exists
   * - Entry has expired (> 30 min old)
   * - Content doesn't match (user edited slide)
   */
  const getCache = useCallback((content: string): string | null => {
    const cached = previewCache.get(slideId);

    if (!cached) {
      return null;
    }

    // Check if expired
    if (Date.now() - cached.timestamp > CACHE_EXPIRY) {
      previewCache.delete(slideId);
      return null;
    }

    // Check if content matches
    if (cached.content !== content) {
      return null;
    }

    return cached.rendered;
  }, [slideId]);

  /**
   * Store preview in cache
   * Implements simple LRU by deleting oldest entry when cache is full
   */
  const setCache = useCallback((content: string, rendered: string) => {
    // Add new entry
    previewCache.set(slideId, {
      content,
      rendered,
      timestamp: Date.now(),
    });

    // Simple LRU: if cache is too large, delete first (oldest) entry
    // Map maintains insertion order, so first entry is oldest
    if (previewCache.size > MAX_CACHE_SIZE) {
      const firstKey = previewCache.keys().next().value;
      if (firstKey) {
        previewCache.delete(firstKey);
      }
    }
  }, [slideId]);

  return { getCache, setCache };
}
