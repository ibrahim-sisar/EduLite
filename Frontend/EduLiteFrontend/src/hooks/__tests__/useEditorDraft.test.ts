import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useEditorDraft } from '../useEditorDraft';
import type { EditorDraft } from '../../types/editor.types';

describe('useEditorDraft', () => {
  const mockDraft: EditorDraft = {
    slideshowId: 123,
    lastSaved: '2024-01-01T00:00:00.000Z',
    lastModified: '2024-01-01T00:01:00.000Z',
    version: 5,
    data: {
      title: 'Test Slideshow',
      description: 'Test Description',
      visibility: 'private',
      subject: 'math',
      language: 'en',
      country: 'US',
      is_published: false,
      slides: [
        {
          tempId: 'slide-1',
          order: 0,
          content: '# Slide 1',
          notes: 'Notes for slide 1',
        },
      ],
    },
  };

  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    vi.clearAllMocks();
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('loadDraft', () => {
    it('should return null when no draft exists', () => {
      const { result } = renderHook(() => useEditorDraft(123));

      const draft = result.current.loadDraft();

      expect(draft).toBeNull();
    });

    it('should load existing draft from localStorage', () => {
      // Save draft to localStorage
      localStorage.setItem('slideshow-draft-123', JSON.stringify(mockDraft));

      const { result } = renderHook(() => useEditorDraft(123));
      const draft = result.current.loadDraft();

      expect(draft).toEqual(mockDraft);
    });

    it('should handle "new" slideshow ID', () => {
      const newDraft = { ...mockDraft, slideshowId: 'new' as const };
      localStorage.setItem('slideshow-draft-new', JSON.stringify(newDraft));

      const { result } = renderHook(() => useEditorDraft('new'));
      const draft = result.current.loadDraft();

      expect(draft).toEqual(newDraft);
      expect(draft?.slideshowId).toBe('new');
    });

    it('should return null for corrupted JSON data', () => {
      // Store invalid JSON
      localStorage.setItem('slideshow-draft-123', 'not valid json {{{');

      const { result } = renderHook(() => useEditorDraft(123));
      const draft = result.current.loadDraft();

      expect(draft).toBeNull();
    });

    it('should return null when localStorage throws error', () => {
      // Mock localStorage.getItem to throw
      const getItemSpy = vi.spyOn(Storage.prototype, 'getItem');
      getItemSpy.mockImplementation(() => {
        throw new Error('localStorage access denied');
      });

      const { result } = renderHook(() => useEditorDraft(123));
      const draft = result.current.loadDraft();

      expect(draft).toBeNull();

      getItemSpy.mockRestore();
    });

    it('should use correct key for different slideshow IDs', () => {
      const draft1 = { ...mockDraft, slideshowId: 111 };
      const draft2 = { ...mockDraft, slideshowId: 222 };

      localStorage.setItem('slideshow-draft-111', JSON.stringify(draft1));
      localStorage.setItem('slideshow-draft-222', JSON.stringify(draft2));

      const { result: result1 } = renderHook(() => useEditorDraft(111));
      const { result: result2 } = renderHook(() => useEditorDraft(222));

      expect(result1.current.loadDraft()?.slideshowId).toBe(111);
      expect(result2.current.loadDraft()?.slideshowId).toBe(222);
    });
  });

  describe('saveDraft', () => {
    it('should save draft to localStorage', () => {
      const { result } = renderHook(() => useEditorDraft(123));

      result.current.saveDraft(mockDraft);

      const stored = localStorage.getItem('slideshow-draft-123');
      expect(stored).toBeTruthy();

      const parsed = JSON.parse(stored!);
      expect(parsed.slideshowId).toBe(123);
      expect(parsed.data.title).toBe('Test Slideshow');
    });

    it('should update lastModified timestamp when saving', () => {
      const { result } = renderHook(() => useEditorDraft(123));

      const beforeSave = new Date().toISOString();
      result.current.saveDraft(mockDraft);
      const afterSave = new Date().toISOString();

      const stored = localStorage.getItem('slideshow-draft-123');
      const parsed = JSON.parse(stored!);

      expect(parsed.lastModified).toBeDefined();
      expect(parsed.lastModified >= beforeSave).toBe(true);
      expect(parsed.lastModified <= afterSave).toBe(true);
    });

    it('should preserve all draft data when saving', () => {
      const { result } = renderHook(() => useEditorDraft(123));

      result.current.saveDraft(mockDraft);

      const stored = localStorage.getItem('slideshow-draft-123');
      const parsed = JSON.parse(stored!);

      expect(parsed.version).toBe(5);
      expect(parsed.data.slides).toHaveLength(1);
      expect(parsed.data.slides[0].content).toBe('# Slide 1');
      expect(parsed.data.slides[0].notes).toBe('Notes for slide 1');
    });

    it('should handle localStorage quota exceeded', () => {
      // Mock setItem to throw quota exceeded error
      const setItemSpy = vi.spyOn(Storage.prototype, 'setItem');
      setItemSpy.mockImplementation(() => {
        throw new DOMException('QuotaExceededError');
      });

      const { result } = renderHook(() => useEditorDraft(123));

      // Should not throw, just log error
      expect(() => result.current.saveDraft(mockDraft)).not.toThrow();

      setItemSpy.mockRestore();
    });

    it('should save different drafts for different slideshow IDs', () => {
      const { result: result1 } = renderHook(() => useEditorDraft(111));
      const { result: result2 } = renderHook(() => useEditorDraft(222));

      const draft1 = { ...mockDraft, slideshowId: 111 };
      const draft2 = { ...mockDraft, slideshowId: 222 };

      result1.current.saveDraft(draft1);
      result2.current.saveDraft(draft2);

      const stored1 = localStorage.getItem('slideshow-draft-111');
      const stored2 = localStorage.getItem('slideshow-draft-222');

      expect(JSON.parse(stored1!).slideshowId).toBe(111);
      expect(JSON.parse(stored2!).slideshowId).toBe(222);
    });

    it('should save draft for "new" slideshow', () => {
      const { result } = renderHook(() => useEditorDraft('new'));

      const newDraft = { ...mockDraft, slideshowId: 'new' as const };
      result.current.saveDraft(newDraft);

      const stored = localStorage.getItem('slideshow-draft-new');
      expect(stored).toBeTruthy();
      expect(JSON.parse(stored!).slideshowId).toBe('new');
    });
  });

  describe('clearDraft', () => {
    it('should remove draft from localStorage', () => {
      // First save a draft
      localStorage.setItem('slideshow-draft-123', JSON.stringify(mockDraft));
      expect(localStorage.getItem('slideshow-draft-123')).toBeTruthy();

      const { result } = renderHook(() => useEditorDraft(123));
      result.current.clearDraft();

      expect(localStorage.getItem('slideshow-draft-123')).toBeNull();
    });

    it('should not throw if draft does not exist', () => {
      const { result } = renderHook(() => useEditorDraft(123));

      expect(() => result.current.clearDraft()).not.toThrow();
    });

    it('should only clear the specific slideshow draft', () => {
      // Save multiple drafts
      localStorage.setItem('slideshow-draft-111', JSON.stringify({ ...mockDraft, slideshowId: 111 }));
      localStorage.setItem('slideshow-draft-222', JSON.stringify({ ...mockDraft, slideshowId: 222 }));

      const { result } = renderHook(() => useEditorDraft(111));
      result.current.clearDraft();

      // Only 111 should be cleared
      expect(localStorage.getItem('slideshow-draft-111')).toBeNull();
      expect(localStorage.getItem('slideshow-draft-222')).toBeTruthy();
    });

    it('should handle localStorage errors gracefully', () => {
      const removeItemSpy = vi.spyOn(Storage.prototype, 'removeItem');
      removeItemSpy.mockImplementation(() => {
        throw new Error('localStorage access denied');
      });

      const { result } = renderHook(() => useEditorDraft(123));

      expect(() => result.current.clearDraft()).not.toThrow();

      removeItemSpy.mockRestore();
    });
  });

  describe('Integration scenarios', () => {
    it('should support save-load-clear workflow', () => {
      const { result } = renderHook(() => useEditorDraft(123));

      // Save
      result.current.saveDraft(mockDraft);

      // Load
      const loaded = result.current.loadDraft();
      expect(loaded?.data.title).toBe('Test Slideshow');

      // Clear
      result.current.clearDraft();

      // Load again should return null
      const loadedAfterClear = result.current.loadDraft();
      expect(loadedAfterClear).toBeNull();
    });

    it('should handle rapid saves (overwrite)', () => {
      const { result } = renderHook(() => useEditorDraft(123));

      const draft1 = { ...mockDraft, data: { ...mockDraft.data, title: 'Version 1' } };
      const draft2 = { ...mockDraft, data: { ...mockDraft.data, title: 'Version 2' } };
      const draft3 = { ...mockDraft, data: { ...mockDraft.data, title: 'Version 3' } };

      result.current.saveDraft(draft1);
      result.current.saveDraft(draft2);
      result.current.saveDraft(draft3);

      const loaded = result.current.loadDraft();
      expect(loaded?.data.title).toBe('Version 3');
    });

    it('should maintain referential stability of hook functions', () => {
      const { result, rerender } = renderHook(() => useEditorDraft(123));

      const loadDraft1 = result.current.loadDraft;
      const saveDraft1 = result.current.saveDraft;
      const clearDraft1 = result.current.clearDraft;

      rerender();

      const loadDraft2 = result.current.loadDraft;
      const saveDraft2 = result.current.saveDraft;
      const clearDraft2 = result.current.clearDraft;

      // Functions should be stable (same reference)
      expect(loadDraft1).toBe(loadDraft2);
      expect(saveDraft1).toBe(saveDraft2);
      expect(clearDraft1).toBe(clearDraft2);
    });
  });
});
