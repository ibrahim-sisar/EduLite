/**
 * Slideshow Viewer Components
 *
 * A presentation viewer with progressive loading, keyboard navigation,
 * and offline capability for low-connectivity environments.
 */

export { default as SlideshowViewer } from "./SlideshowViewer";
export { default as SlideDisplay } from "./SlideDisplay";
export { default as SlideProgress } from "./SlideProgress";

export type {
  SlideshowViewerProps,
  SlideDisplayProps,
  SlideProgressProps,
} from "./types";
