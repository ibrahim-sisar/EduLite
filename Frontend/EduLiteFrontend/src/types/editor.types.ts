/**
 * Type definitions for the Slideshow Editor
 */

export interface EditorSlide {
  id?: number; // Undefined for new slides not yet saved to backend
  tempId: string; // Client-side UUID for tracking
  order: number;
  content: string; // Raw markdown
  rendered_content?: string; // Cached from backend preview
}

export interface EditorDraft {
  slideshowId: number | "new";
  lastSaved: string; // ISO timestamp
  lastModified: string; // ISO timestamp
  version?: number; // Server version (undefined for new slideshows)
  data: {
    title: string;
    description: string;
    visibility: "public" | "unlisted" | "private";
    subject: string | null;
    language: string | null;
    country: string | null;
    is_published: boolean;
    slides: EditorSlide[];
  };
}

export type SaveStatus = "idle" | "saving" | "saved" | "error" | "offline";

export interface AutoSaveOptions {
  delay: number;
  enabled: boolean;
  isOnline: boolean;
}

export interface EditorState {
  slideshow: EditorDraft | null;
  selectedSlideId: string | null;
  saving: boolean;
  saveError: string | null;
  lastSaved: Date | null;
  isDirty: boolean;
  isOnline: boolean;
}
