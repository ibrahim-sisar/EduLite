import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook } from '@testing-library/react';
import { usePreviewCache } from '../usePreviewCache';

describe('usePreviewCache', () => {
  beforeEach(() => {
    // Clear the cache before each test by creating a new hook and letting it reset
    vi.clearAllMocks();
  });

  describe('getCache', () => {
    it('should return null for cache miss', () => {
      const { result } = renderHook(() => usePreviewCache('slide-1'));

      const cached = result.current.getCache('# Hello');

      expect(cached).toBeNull();
    });

    it('should return cached content on cache hit', () => {
      const { result } = renderHook(() => usePreviewCache('slide-1'));

      // Set cache
      result.current.setCache('# Hello', '<h1>Hello</h1>');

      // Get cache
      const cached = result.current.getCache('# Hello');

      expect(cached).toBe('<h1>Hello</h1>');
    });

    it('should return null if content does not match', () => {
      const { result } = renderHook(() => usePreviewCache('slide-1'));

      // Cache for different content
      result.current.setCache('# Hello', '<h1>Hello</h1>');

      // Try to get with different content
      const cached = result.current.getCache('# Goodbye');

      expect(cached).toBeNull();
    });

    it('should return null if cache has expired (>30 min)', () => {
      const { result } = renderHook(() => usePreviewCache('slide-1'));

      // Mock Date.now to control time
      const originalNow = Date.now;
      const startTime = 1000000000;
      Date.now = vi.fn(() => startTime);

      // Set cache at startTime
      result.current.setCache('# Hello', '<h1>Hello</h1>');

      // Move time forward 31 minutes
      const thirtyOneMinutes = 31 * 60 * 1000;
      Date.now = vi.fn(() => startTime + thirtyOneMinutes);

      // Should return null (expired)
      const cached = result.current.getCache('# Hello');

      expect(cached).toBeNull();

      // Restore Date.now
      Date.now = originalNow;
    });

    it('should return cached content within 30 min expiry', () => {
      const { result } = renderHook(() => usePreviewCache('slide-1'));

      const originalNow = Date.now;
      const startTime = 1000000000;
      Date.now = vi.fn(() => startTime);

      result.current.setCache('# Hello', '<h1>Hello</h1>');

      // Move time forward 29 minutes (still valid)
      const twentyNineMinutes = 29 * 60 * 1000;
      Date.now = vi.fn(() => startTime + twentyNineMinutes);

      const cached = result.current.getCache('# Hello');

      expect(cached).toBe('<h1>Hello</h1>');

      Date.now = originalNow;
    });

    it('should isolate cache by slideId', () => {
      const { result: slide1 } = renderHook(() => usePreviewCache('slide-1'));
      const { result: slide2 } = renderHook(() => usePreviewCache('slide-2'));

      slide1.current.setCache('# Content', '<h1>Content</h1>');

      // slide-2 should not have access to slide-1's cache
      const cached = slide2.current.getCache('# Content');

      expect(cached).toBeNull();
    });
  });

  describe('setCache', () => {
    it('should store content in cache', () => {
      const { result } = renderHook(() => usePreviewCache('slide-1'));

      result.current.setCache('# Test', '<h1>Test</h1>');

      const cached = result.current.getCache('# Test');
      expect(cached).toBe('<h1>Test</h1>');
    });

    it('should overwrite existing cache for same content', () => {
      const { result } = renderHook(() => usePreviewCache('slide-1'));

      result.current.setCache('# Test', '<h1>Old</h1>');
      result.current.setCache('# Test', '<h1>New</h1>');

      const cached = result.current.getCache('# Test');
      expect(cached).toBe('<h1>New</h1>');
    });

    it('should update timestamp on re-cache', () => {
      const { result } = renderHook(() => usePreviewCache('slide-1'));

      const originalNow = Date.now;
      const startTime = 1000000000;
      Date.now = vi.fn(() => startTime);

      // First cache
      result.current.setCache('# Test', '<h1>Test</h1>');

      // Move time forward 10 minutes
      Date.now = vi.fn(() => startTime + 10 * 60 * 1000);

      // Re-cache (updates timestamp)
      result.current.setCache('# Test', '<h1>Test</h1>');

      // Move time forward another 25 minutes (35 total, but only 25 from re-cache)
      Date.now = vi.fn(() => startTime + 35 * 60 * 1000);

      // Should still be valid (25 min from re-cache < 30 min expiry)
      const cached = result.current.getCache('# Test');
      expect(cached).toBe('<h1>Test</h1>');

      Date.now = originalNow;
    });
  });

  describe('LRU eviction', () => {
    it('should evict oldest entry when cache exceeds 20 items', () => {
      // Create 20 different slides (each slideId is a separate cache entry)
      const slides = [];
      for (let i = 1; i <= 20; i++) {
        const { result } = renderHook(() => usePreviewCache(`slide-${i}`));
        slides.push(result);
        result.current.setCache(`content-${i}`, `<p>rendered-${i}</p>`);
      }

      // First slide should still be cached
      expect(slides[0].current.getCache('content-1')).toBe('<p>rendered-1</p>');

      // Add 21st slide (should evict first)
      const { result: slide21 } = renderHook(() => usePreviewCache('slide-21'));
      slide21.current.setCache('content-21', '<p>rendered-21</p>');

      // First slide should be evicted
      expect(slides[0].current.getCache('content-1')).toBeNull();

      // 21st slide should be cached
      expect(slide21.current.getCache('content-21')).toBe('<p>rendered-21</p>');

      // Slides 2-20 should still be cached
      expect(slides[1].current.getCache('content-2')).toBe('<p>rendered-2</p>');
      expect(slides[19].current.getCache('content-20')).toBe('<p>rendered-20</p>');
    });

    it('should keep last 20 items when adding many', () => {
      // Create 50 different slides
      const slides = [];
      for (let i = 1; i <= 50; i++) {
        const { result } = renderHook(() => usePreviewCache(`slide-${i}`));
        slides.push(result);
        result.current.setCache(`content-${i}`, `<p>rendered-${i}</p>`);
      }

      // First 30 should be evicted
      for (let i = 0; i < 30; i++) {
        expect(slides[i].current.getCache(`content-${i + 1}`)).toBeNull();
      }

      // Last 20 should remain
      for (let i = 30; i < 50; i++) {
        expect(slides[i].current.getCache(`content-${i + 1}`)).toBe(`<p>rendered-${i + 1}</p>`);
      }
    });

    it('should treat each slideId as separate cache entry for LRU', () => {
      // Fill cache with 20 different slides
      const slides = [];
      for (let i = 1; i <= 20; i++) {
        const { result } = renderHook(() => usePreviewCache(`slide-${i}`));
        slides.push(result);
        result.current.setCache(`content-${i}`, `<p>slide-${i}</p>`);
      }

      // Add 21st slide (different slideId, so it's a separate cache entry)
      const { result: slide21 } = renderHook(() => usePreviewCache('slide-21'));
      slide21.current.setCache('content-21', '<p>slide-21</p>');

      // Adding slide-21 should trigger eviction since we now have 21 total entries
      // First slide should be evicted
      expect(slides[0].current.getCache('content-1')).toBeNull();

      // slide-21 entry should exist
      expect(slide21.current.getCache('content-21')).toBe('<p>slide-21</p>');

      // Other slides should still exist
      expect(slides[1].current.getCache('content-2')).toBe('<p>slide-2</p>');
      expect(slides[19].current.getCache('content-20')).toBe('<p>slide-20</p>');
    });
  });

  describe('Edge cases', () => {
    it('should handle empty content', () => {
      const { result } = renderHook(() => usePreviewCache('slide-1'));

      result.current.setCache('', '');
      const cached = result.current.getCache('');

      expect(cached).toBe('');
    });

    it('should handle very large content', () => {
      const { result } = renderHook(() => usePreviewCache('slide-1'));

      const largeContent = '# Title\n' + 'x'.repeat(10000);
      const largeRendered = '<h1>Title</h1>' + '<p>' + 'x'.repeat(10000) + '</p>';

      result.current.setCache(largeContent, largeRendered);
      const cached = result.current.getCache(largeContent);

      expect(cached).toBe(largeRendered);
    });

    it('should handle special characters in content', () => {
      const { result } = renderHook(() => usePreviewCache('slide-1'));

      const content = '# Hello 你好 مرحبا 🎉';
      const rendered = '<h1>Hello 你好 مرحبا 🎉</h1>';

      result.current.setCache(content, rendered);
      const cached = result.current.getCache(content);

      expect(cached).toBe(rendered);
    });

    it('should maintain referential stability of hook functions', () => {
      const { result, rerender } = renderHook(() => usePreviewCache('slide-1'));

      const getCache1 = result.current.getCache;
      const setCache1 = result.current.setCache;

      rerender();

      const getCache2 = result.current.getCache;
      const setCache2 = result.current.setCache;

      expect(getCache1).toBe(getCache2);
      expect(setCache1).toBe(setCache2);
    });
  });

  describe('Integration scenarios', () => {
    it('should support rapid cache updates for same slide', () => {
      const { result } = renderHook(() => usePreviewCache('slide-1'));

      // Simulate user typing rapidly - each setCache overwrites previous for same slideId
      result.current.setCache('# H', '<h1>H</h1>');
      result.current.setCache('# He', '<h1>He</h1>');
      result.current.setCache('# Hel', '<h1>Hel</h1>');
      result.current.setCache('# Hell', '<h1>Hell</h1>');
      result.current.setCache('# Hello', '<h1>Hello</h1>');

      // Only last version should be cached (others were overwritten)
      expect(result.current.getCache('# Hello')).toBe('<h1>Hello</h1>');

      // Previous versions should NOT be cached (content mismatch)
      expect(result.current.getCache('# Hell')).toBeNull();
      expect(result.current.getCache('# H')).toBeNull();
    });

    it('should support switching between slides', () => {
      const { result: slide1 } = renderHook(() => usePreviewCache('slide-1'));
      const { result: slide2 } = renderHook(() => usePreviewCache('slide-2'));
      const { result: slide3 } = renderHook(() => usePreviewCache('slide-3'));

      // Cache content for each slide
      slide1.current.setCache('# Slide 1', '<h1>Slide 1</h1>');
      slide2.current.setCache('# Slide 2', '<h1>Slide 2</h1>');
      slide3.current.setCache('# Slide 3', '<h1>Slide 3</h1>');

      // Each slide should have its own cached content
      expect(slide1.current.getCache('# Slide 1')).toBe('<h1>Slide 1</h1>');
      expect(slide2.current.getCache('# Slide 2')).toBe('<h1>Slide 2</h1>');
      expect(slide3.current.getCache('# Slide 3')).toBe('<h1>Slide 3</h1>');

      // Cross-slide access should fail
      expect(slide1.current.getCache('# Slide 2')).toBeNull();
      expect(slide2.current.getCache('# Slide 3')).toBeNull();
    });
  });
});
