import React, { useState, useEffect, useCallback, useRef } from "react";
import toast from "react-hot-toast";
import {
  HiXMark,
  HiArrowLeft,
  HiArrowRight,
  HiArrowsPointingOut,
  HiArrowsPointingIn,
  HiPencil,
} from "react-icons/hi2";
import { HiCog, HiQuestionMarkCircle } from "react-icons/hi";
import { getSlideshowDetail, getSlide } from "../../services/slideshowApi";
import type { Slide, SlideViewOnly } from "../../types/slideshow.types";
import type { SlideshowViewerProps } from "./types";
import SlideDisplay from "./SlideDisplay";
import SlideProgress from "./SlideProgress";
import SpeakerNotes from "./SpeakerNotes";
import PresentationSettingsModal from "./PresentationSettingsModal";
import PresentationHelpModal from "./PresentationHelpModal";

/**
 * SlideshowViewer Component
 *
 * Main presentation viewer with:
 * - Progressive loading (first 3 slides immediate, rest in background)
 * - Keyboard navigation (arrows, space, escape, N for notes)
 * - Fullscreen support (optional)
 * - Offline capability (loads ALL slides, works without network)
 * - Speaker notes panel
 */
const SlideshowViewer: React.FC<SlideshowViewerProps> = ({
  slideshowId,
  initialSlide = 0,
  showNotes: showNotesInitial = false,
  onExit,
  allowFullscreen = false,
}) => {
  // State management
  const [currentIndex, setCurrentIndex] = useState<number>(initialSlide);
  const [slides, setSlides] = useState<Map<number, Slide | SlideViewOnly>>(new Map());
  const [showNotes, setShowNotes] = useState<boolean>(showNotesInitial);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
  const [slideCount, setSlideCount] = useState<number>(0);
  const [slideshowTitle, setSlideshowTitle] = useState<string>("");
  const [remainingSlideIds, setRemainingSlideIds] = useState<number[]>([]);
  const [settingsOpen, setSettingsOpen] = useState<boolean>(false);
  const [helpOpen, setHelpOpen] = useState<boolean>(false);

  const containerRef = useRef<HTMLDivElement>(null);

  // Get current slide
  const currentSlide = slides.get(currentIndex) || null;
  const currentSlideNotes: string | null =
    currentSlide && "notes" in currentSlide
      ? (currentSlide.notes as string | null)
      : null;

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
        setSlideshowTitle(data.title);
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
        setError(err instanceof Error ? err.message : "Failed to load slideshow");
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
            .catch((error) => ({ slideId, slide: null, error }))
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
   * Navigation functions
   */
  const goToNextSlide = useCallback(() => {
    setCurrentIndex((prev) => Math.min(prev + 1, slideCount - 1));
  }, [slideCount]);

  const goToPreviousSlide = useCallback(() => {
    setCurrentIndex((prev) => Math.max(prev - 1, 0));
  }, []);

  const goToSlide = useCallback((index: number) => {
    setCurrentIndex(Math.max(0, Math.min(index, slideCount - 1)));
  }, [slideCount]);

  const toggleNotes = useCallback(() => {
    setShowNotes((prev) => !prev);
  }, []);

  const handleEdit = useCallback(() => {
    // TODO: Navigate to editor when implemented
    // navigate(`/slideshows/${slideshowId}/edit`);
    toast("Editor coming soon!", {
      icon: "✏️",
      duration: 3000,
    });
  }, [slideshowId]);

  /**
   * Fullscreen handling
   */
  const toggleFullscreen = useCallback(async () => {
    if (!containerRef.current) return;

    try {
      if (!document.fullscreenElement) {
        await containerRef.current.requestFullscreen();
        setIsFullscreen(true);
      } else {
        await document.exitFullscreen();
        setIsFullscreen(false);
      }
    } catch (err) {
      console.error("Fullscreen error:", err);
      toast.error("Failed to toggle fullscreen");
    }
  }, []);

  // Listen for fullscreen changes (e.g., user presses Esc)
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener("fullscreenchange", handleFullscreenChange);
    return () => document.removeEventListener("fullscreenchange", handleFullscreenChange);
  }, []);

  /**
   * Keyboard navigation
   */
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case "ArrowRight":
        case " ":
          e.preventDefault();
          goToNextSlide();
          break;
        case "ArrowLeft":
        case "Backspace":
          e.preventDefault();
          goToPreviousSlide();
          break;
        case "Escape":
          e.preventDefault();
          if (document.fullscreenElement) {
            document.exitFullscreen();
          } else {
            onExit?.();
          }
          break;
        case "n":
        case "N":
          e.preventDefault();
          toggleNotes();
          break;
        case "Home":
          e.preventDefault();
          goToSlide(0);
          break;
        case "End":
          e.preventDefault();
          goToSlide(slideCount - 1);
          break;
        case "f":
        case "F":
          if (allowFullscreen) {
            e.preventDefault();
            toggleFullscreen();
          }
          break;
        default:
          // Number keys (1-9) for quick jump
          if (e.key >= "1" && e.key <= "9") {
            const slideNum = parseInt(e.key, 10) - 1;
            if (slideNum < slideCount) {
              e.preventDefault();
              goToSlide(slideNum);
            }
          }
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [
    goToNextSlide,
    goToPreviousSlide,
    goToSlide,
    toggleNotes,
    toggleFullscreen,
    onExit,
    slideCount,
    allowFullscreen,
  ]);

  /**
   * Error state
   */
  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
        <div className="bg-red-900/20 border border-red-500/50 rounded-2xl p-8 max-w-md text-center">
          <h2 className="text-2xl font-light text-red-400 mb-4">Error Loading Slideshow</h2>
          <p className="text-gray-300 mb-6">{error}</p>
          {onExit && (
            <button
              onClick={onExit}
              className="px-6 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors cursor-pointer"
            >
              Go Back
            </button>
          )}
        </div>
      </div>
    );
  }

  /**
   * Loading state
   */
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-500 mx-auto mb-6"></div>
          <p className="text-xl text-gray-300 font-light">Loading presentation...</p>
        </div>
      </div>
    );
  }

  /**
   * Main viewer UI
   */
  const loadedSlides = Array.from({ length: slideCount }, (_, i) => slides.has(i));
  const isCurrentSlideLoading = !slides.has(currentIndex);

  return (
    <div
      ref={containerRef}
      className="min-h-screen bg-white dark:bg-black flex flex-col"
    >
      {/* Header / Controls */}
      <div className="flex items-center justify-between px-6 py-4 bg-white/90 dark:bg-black/80 backdrop-blur-lg border-b border-gray-200 dark:border-gray-700/30">
        {/* Title */}
        <h2 className="text-xl font-light text-gray-900 dark:text-white truncate max-w-md">
          {slideshowTitle}
        </h2>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          {/* Edit Button (Always show, TODO: check ownership on backend when editor exists) */}
          <button
            onClick={handleEdit}
            className="p-2 rounded-lg bg-gray-200 dark:bg-gray-800 hover:bg-blue-500 dark:hover:bg-blue-600 text-gray-700 dark:text-gray-300 hover:text-white transition-colors cursor-pointer"
            aria-label="Edit slideshow"
            title="Edit slideshow"
          >
            <HiPencil className="w-5 h-5" />
          </button>

          {/* Settings Button */}
          <button
            onClick={() => setSettingsOpen(true)}
            className="p-2 rounded-lg bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors cursor-pointer"
            aria-label="Settings"
            title="Settings"
          >
            <HiCog className="w-5 h-5" />
          </button>

          {/* Help Button */}
          <button
            onClick={() => setHelpOpen(true)}
            className="p-2 rounded-lg bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors cursor-pointer"
            aria-label="Help"
            title="Help"
          >
            <HiQuestionMarkCircle className="w-5 h-5" />
          </button>

          {/* Fullscreen Toggle */}
          {allowFullscreen && (
            <button
              onClick={toggleFullscreen}
              className="p-2 rounded-lg bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors cursor-pointer"
              aria-label={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
              title={isFullscreen ? "Exit fullscreen (F)" : "Enter fullscreen (F)"}
            >
              {isFullscreen ? (
                <HiArrowsPointingIn className="w-5 h-5" />
              ) : (
                <HiArrowsPointingOut className="w-5 h-5" />
              )}
            </button>
          )}

          {/* Exit Button */}
          {onExit && (
            <button
              onClick={onExit}
              className="p-2 rounded-lg bg-gray-200 dark:bg-gray-800 hover:bg-red-600 dark:hover:bg-red-700 text-gray-700 dark:text-gray-300 hover:text-white transition-colors cursor-pointer"
              aria-label="Exit presentation"
              title="Exit (Esc)"
            >
              <HiXMark className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex items-center justify-center overflow-hidden relative">
        <div className="w-full h-full">
          {/* Slide Display */}
          <SlideDisplay
            slide={currentSlide}
            isLoading={isCurrentSlideLoading}
            slideNumber={currentIndex + 1}
            totalSlides={slideCount}
          />
        </div>

        {/* Navigation Arrows (visible on hover on desktop) */}
        <div className="absolute left-4 top-1/2 -translate-y-1/2 opacity-0 hover:opacity-100 transition-opacity hidden md:block">
          <button
            onClick={goToPreviousSlide}
            disabled={currentIndex === 0}
            className="p-4 rounded-full bg-gray-800/80 hover:bg-gray-700/80 backdrop-blur-lg text-gray-300 hover:text-white transition-all disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer"
            aria-label="Previous slide"
          >
            <HiArrowLeft className="w-6 h-6" />
          </button>
        </div>

        <div className="absolute right-4 top-1/2 -translate-y-1/2 opacity-0 hover:opacity-100 transition-opacity hidden md:block">
          <button
            onClick={goToNextSlide}
            disabled={currentIndex === slideCount - 1}
            className="p-4 rounded-full bg-gray-800/80 hover:bg-gray-700/80 backdrop-blur-lg text-gray-300 hover:text-white transition-all disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer"
            aria-label="Next slide"
          >
            <HiArrowRight className="w-6 h-6" />
          </button>
        </div>
      </div>

      {/* Speaker Notes Panel */}
      <SpeakerNotes
        notes={currentSlideNotes}
        isVisible={showNotes}
        onToggle={toggleNotes}
      />

      {/* Progress Bar */}
      <SlideProgress
        currentIndex={currentIndex}
        totalSlides={slideCount}
        loadedSlides={loadedSlides}
        onSlideClick={goToSlide}
      />

      {/* Settings Modal */}
      <PresentationSettingsModal
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
      />

      {/* Help Modal */}
      <PresentationHelpModal
        isOpen={helpOpen}
        onClose={() => setHelpOpen(false)}
        allowFullscreen={allowFullscreen}
      />
    </div>
  );
};

export default SlideshowViewer;
