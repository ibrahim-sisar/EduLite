import { useCallback } from 'react';
import type { EditorDraft } from '../types/editor.types';

/**
 * Hook for managing editor drafts in localStorage
 * @param slideshowId - ID of the slideshow ('new' for unsaved slideshows)
 * @returns Functions to load, save, and clear drafts
 */
export function useEditorDraft(slideshowId: number | 'new') {
  const key = `slideshow-draft-${slideshowId}`;

  const loadDraft = useCallback((): EditorDraft | null => {
    try {
      const stored = localStorage.getItem(key);
      if (!stored) return null;

      const draft = JSON.parse(stored) as EditorDraft;
      return draft;
    } catch (error) {
      console.error('Error loading draft from localStorage:', error);
      return null;
    }
  }, [key]);

  const saveDraft = useCallback((draft: EditorDraft) => {
    try {
      const draftToSave = {
        ...draft,
        lastModified: new Date().toISOString(),
      };
      localStorage.setItem(key, JSON.stringify(draftToSave));
    } catch (error) {
      console.error('Error saving draft to localStorage:', error);
    }
  }, [key]);

  const clearDraft = useCallback(() => {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Error clearing draft from localStorage:', error);
    }
  }, [key]);

  return { loadDraft, saveDraft, clearDraft };
}
