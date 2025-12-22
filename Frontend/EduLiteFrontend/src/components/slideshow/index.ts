/**
 * Slideshow Viewer Components
 *
 * A presentation viewer with progressive loading, keyboard navigation,
 * and offline capability for low-connectivity environments.
 */

export { default as SlideshowViewer } from "./SlideshowViewer";
export { default as SlideDisplay } from "./SlideDisplay";
export { default as SlideProgress } from "./SlideProgress";
export { default as SpeakerNotes } from "./SpeakerNotes";

export type {
  SlideshowViewerProps,
  SlideDisplayProps,
  SlideProgressProps,
  SpeakerNotesProps,
} from "./types";
