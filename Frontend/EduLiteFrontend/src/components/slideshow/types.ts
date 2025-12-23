import type { Slide, SlideViewOnly } from "../../types/slideshow.types";

/**
 * Props for the main SlideshowViewer component
 */
export interface SlideshowViewerProps {
  /** The ID of the slideshow to display */
  slideshowId: number;

  /** The index of the slide to start with (0-based) */
  initialSlide?: number;

  /** Whether to show speaker notes by default */
  showNotes?: boolean;

  /** Callback when user exits the viewer (e.g., via Escape key) */
  onExit?: () => void;

  /** Whether to allow fullscreen mode (shows fullscreen button) */
  allowFullscreen?: boolean;
}

/**
 * Props for the SlideDisplay component
 */
export interface SlideDisplayProps {
  /** The slide to display (or null if loading) */
  slide: Slide | SlideViewOnly | null;

  /** Whether the slide is currently loading */
  isLoading: boolean;

  /** Current slide number (1-based for display) */
  slideNumber: number;

  /** Total number of slides */
  totalSlides: number;
}

/**
 * Props for the SlideProgress component
 */
export interface SlideProgressProps {
  /** Current slide index (0-based) */
  currentIndex: number;

  /** Total number of slides */
  totalSlides: number;

  /** Array indicating which slides are loaded (by index) */
  loadedSlides: boolean[];

  /** Callback when a slide is clicked */
  onSlideClick: (index: number) => void;
}

/**
 * Props for the SpeakerNotes component
 */
export interface SpeakerNotesProps {
  /** The notes content to display */
  notes: string | null;

  /** Whether the notes panel is visible */
  isVisible: boolean;

  /** Callback to toggle notes visibility */
  onToggle: () => void;
}
