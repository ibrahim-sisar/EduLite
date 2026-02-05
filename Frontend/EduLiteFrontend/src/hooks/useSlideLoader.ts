import { useState, useEffect } from "react";
import toast from "react-hot-toast";
import { getSlideshowDetail, getSlide } from "../services/slideshowApi";
import type { Slide, SlideViewOnly } from "../types/slideshow.types";

export interface SlideshowMetadata {
  /** Slideshow title */
  title: string;
  /** Author's username */
  author: string;
  /** Subject code (e.g., 'cs', 'math') */
  subject: string | null;
}

export interface UseSlideLoaderReturn {
  /** Map of slides indexed by order */
  slides: Map<number, Slide | SlideViewOnly>;
  /** Total number of slides */
  slideCount: number;
  /** Whether initial slides are loading */
  isLoading: boolean;
  /** Error message if loading failed */
  error: string | null;
  /** Slideshow metadata */
  metadata: SlideshowMetadata;
  /** Check if a specific slide is loaded */
  isSlideLoaded: (index: number) => boolean;
  /** Get array of loaded status for all slides */
  getLoadedSlides: () => boolean[];
}

/**
 * Hook for loading slideshow data with progressive loading.
 *
 * Initially loads the first 3 slides, then loads remaining slides
 * in the background in batches.
 *
 * @example
 * ```tsx
 * const {
 *   slides,
 *   slideCount,
 *   isLoading,
 *   error,
 *   metadata,
 *   isSlideLoaded,
 * } = useSlideLoader(slideshowId);
 * ```
 */
export function useSlideLoader(slideshowId: number): UseSlideLoaderReturn {
  const [slides, setSlides] = useState<Map<number, Slide | SlideViewOnly>>(
    new Map()
  );
  const [slideCount, setSlideCount] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<SlideshowMetadata>({
    title: "",
    author: "",
    subject: null,
  });
  const [remainingSlideIds, setRemainingSlideIds] = useState<number[]>([]);

  /**
   * Initial load: Fetch first 3 slides immediately
   */
  useEffect(() => {
    const loadInitialSlides = async () => {
      setIsLoading(true);
      setError(null);

      try {
        // Fetch first 3 slides
        const data = await getSlideshowDetail(slideshowId, 3);

        // Store slideshow metadata
        setSlideCount(data.slide_count);
        setMetadata({
          title: data.title,
          author: data.created_by_username,
          subject: data.subject,
        });
        setRemainingSlideIds(data.remaining_slide_ids);

        // Store initial slides in Map (indexed by order)
        const initialSlides = new Map<number, Slide | SlideViewOnly>();
        data.slides.forEach((slide) => {
          initialSlides.set(slide.order, slide);
        });
        setSlides(initialSlides);

        setIsLoading(false);
      } catch (err) {
        console.error("Failed to load slideshow:", err);
        const errorMessage =
          err instanceof Error ? err.message : "Failed to load slideshow";
        setError(errorMessage);
        setIsLoading(false);
        toast.error("Failed to load slideshow");
      }
    };

    loadInitialSlides();
  }, [slideshowId]);

  /**
   * Background loading: Fetch remaining slides progressively
   */
  useEffect(() => {
    if (remainingSlideIds.length === 0) return;

    const loadRemainingSlides = async () => {
      // Load remaining slides in parallel (batch of 5 at a time)
      const batchSize = 5;
      const idsToLoad = [...remainingSlideIds];

      for (let i = 0; i < idsToLoad.length; i += batchSize) {
        const batch = idsToLoad.slice(i, i + batchSize);

        // Fetch batch in parallel
        const promises = batch.map((slideId) =>
          getSlide(slideshowId, slideId)
            .then((slide) => ({ slideId, slide, error: null }))
            .catch((fetchError) => ({ slideId, slide: null, error: fetchError }))
        );

        const results = await Promise.all(promises);

        // Store fetched slides
        setSlides((prev) => {
          const newMap = new Map(prev);
          results.forEach(({ slide }) => {
            if (slide) {
              newMap.set(slide.order, slide);
            }
          });
          return newMap;
        });
      }
    };

    loadRemainingSlides();
  }, [remainingSlideIds, slideshowId]);

  /**
   * Check if a specific slide is loaded
   */
  const isSlideLoaded = (index: number): boolean => {
    return slides.has(index);
  };

  /**
   * Get array of loaded status for all slides
   */
  const getLoadedSlides = (): boolean[] => {
    return Array.from({ length: slideCount }, (_, i) => slides.has(i));
  };

  return {
    slides,
    slideCount,
    isLoading,
    error,
    metadata,
    isSlideLoaded,
    getLoadedSlides,
  };
}
