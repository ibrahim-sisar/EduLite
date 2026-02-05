import { useState, useCallback } from "react";

export interface UseSlideNavigationOptions {
  /** Total number of slides */
  slideCount: number;
  /** Initial slide index (0-based) */
  initialSlide?: number;
}

export interface UseSlideNavigationReturn {
  /** Current slide index (0-based) */
  currentIndex: number;
  /** Navigate to a specific slide by index */
  goToSlide: (index: number) => void;
  /** Navigate to the next slide */
  next: () => void;
  /** Navigate to the previous slide */
  prev: () => void;
  /** Whether currently on the first slide */
  isFirst: boolean;
  /** Whether currently on the last slide */
  isLast: boolean;
}

/**
 * Hook for managing slide navigation state and actions.
 *
 * Provides navigation functions with automatic bounds checking.
 *
 * @example
 * ```tsx
 * const { currentIndex, next, prev, isFirst, isLast } = useSlideNavigation({
 *   slideCount: 10,
 *   initialSlide: 0,
 * });
 * ```
 */
export function useSlideNavigation({
  slideCount,
  initialSlide = 0,
}: UseSlideNavigationOptions): UseSlideNavigationReturn {
  // Start with initialSlide - don't clamp during initialization
  // This allows the initial slide to be set before slideCount is known
  const [currentIndex, setCurrentIndex] = useState<number>(
    Math.max(0, initialSlide),
  );

  const goToSlide = useCallback(
    (index: number) => {
      if (slideCount === 0) return;
      setCurrentIndex(Math.max(0, Math.min(index, slideCount - 1)));
    },
    [slideCount],
  );

  const next = useCallback(() => {
    if (slideCount === 0) return;
    setCurrentIndex((prev) => Math.min(prev + 1, slideCount - 1));
  }, [slideCount]);

  const prev = useCallback(() => {
    setCurrentIndex((prev) => Math.max(prev - 1, 0));
  }, []);

  // Clamp currentIndex to valid range for consumers
  // This ensures that when slideCount changes, the index is always valid
  const effectiveIndex =
    slideCount === 0 ? currentIndex : Math.min(currentIndex, slideCount - 1);
  const isFirst = effectiveIndex === 0;
  const isLast = slideCount === 0 ? true : effectiveIndex === slideCount - 1;

  return {
    currentIndex: effectiveIndex,
    goToSlide,
    next,
    prev,
    isFirst,
    isLast,
  };
}
