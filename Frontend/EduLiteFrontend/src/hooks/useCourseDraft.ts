import { useCallback } from "react";

export interface CourseFormData {
  title: string;
  outline: string;
  subject: string;
  language: string;
  country: string;
  visibility: "public" | "restricted" | "private";
  start_date: string;
  end_date: string;
  allow_join_requests: boolean;
}

export interface CourseDraft {
  courseId: number | "new";
  lastSaved: string;
  lastModified: string;
  data: CourseFormData;
}

/**
 * Hook for managing course drafts in localStorage
 * @param courseId - ID of the course ('new' for unsaved courses)
 * @returns Functions to load, save, and clear drafts
 */
export function useCourseDraft(courseId: number | "new") {
  const key = `course-draft-${courseId}`;

  const loadDraft = useCallback((): CourseDraft | null => {
    try {
      const stored = localStorage.getItem(key);
      if (!stored) return null;

      const draft = JSON.parse(stored) as CourseDraft;
      return draft;
    } catch (error) {
      console.error("Error loading course draft from localStorage:", error);
      return null;
    }
  }, [key]);

  const saveDraft = useCallback(
    (draft: CourseDraft) => {
      try {
        const draftToSave = {
          ...draft,
          lastModified: new Date().toISOString(),
        };
        localStorage.setItem(key, JSON.stringify(draftToSave));
      } catch (error) {
        console.error("Error saving course draft to localStorage:", error);
      }
    },
    [key],
  );

  const clearDraft = useCallback(() => {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error("Error clearing course draft from localStorage:", error);
    }
  }, [key]);

  return { loadDraft, saveDraft, clearDraft };
}
