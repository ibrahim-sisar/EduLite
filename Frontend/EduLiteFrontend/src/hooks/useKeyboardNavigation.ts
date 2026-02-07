import { useEffect } from "react";

export interface UseKeyboardNavigationOptions {
  /** Navigate to next slide */
  onNext: () => void;
  /** Navigate to previous slide */
  onPrev: () => void;
  /** Navigate to specific slide by index */
  onGoToSlide: (index: number) => void;
  /** Toggle fullscreen mode */
  onToggleFullscreen?: () => void;
  /** Exit the presentation */
  onExit?: () => void;
  /** Total number of slides (for number key navigation) */
  slideCount: number;
  /** Whether fullscreen is allowed */
  allowFullscreen?: boolean;
  /** Whether keyboard navigation is enabled */
  enabled?: boolean;
}

/**
 * Hook for handling keyboard navigation in the slideshow viewer.
 *
 * Supports:
 * - Arrow Right / Space: Next slide
 * - Arrow Left / Backspace: Previous slide
 * - Escape: Exit fullscreen or presentation
 * - F: Toggle fullscreen (when allowed)
 * - Home: Go to first slide
 * - End: Go to last slide
 * - 1-9: Quick jump to slide (1-indexed)
 *
 * @example
 * ```tsx
 * useKeyboardNavigation({
 *   onNext: navigation.next,
 *   onPrev: navigation.prev,
 *   onGoToSlide: navigation.goToSlide,
 *   onToggleFullscreen: presentation.toggleFullscreen,
 *   onExit: handleExit,
 *   slideCount: 10,
 *   allowFullscreen: true,
 * });
 * ```
 */
export function useKeyboardNavigation({
  onNext,
  onPrev,
  onGoToSlide,
  onToggleFullscreen,
  onExit,
  slideCount,
  allowFullscreen = false,
  enabled = true,
}: UseKeyboardNavigationOptions): void {
  useEffect(() => {
    if (!enabled) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case "ArrowRight":
        case " ":
          e.preventDefault();
          onNext();
          break;

        case "ArrowLeft":
        case "Backspace":
          e.preventDefault();
          onPrev();
          break;

        case "Escape":
          e.preventDefault();
          if (document.fullscreenElement) {
            document.exitFullscreen();
          } else {
            onExit?.();
          }
          break;

        case "Home":
          e.preventDefault();
          onGoToSlide(0);
          break;

        case "End":
          e.preventDefault();
          onGoToSlide(slideCount - 1);
          break;

        case "f":
        case "F":
          if (allowFullscreen && onToggleFullscreen) {
            e.preventDefault();
            onToggleFullscreen();
          }
          break;

        default:
          // Number keys (1-9) for quick jump
          if (e.key >= "1" && e.key <= "9") {
            const slideNum = parseInt(e.key, 10) - 1; // Convert to 0-indexed
            if (slideNum < slideCount) {
              e.preventDefault();
              onGoToSlide(slideNum);
            }
          }
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [
    onNext,
    onPrev,
    onGoToSlide,
    onToggleFullscreen,
    onExit,
    slideCount,
    allowFullscreen,
    enabled,
  ]);
}
